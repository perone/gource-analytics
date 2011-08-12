import time
import datetime

import gdata.analytics.client
import gdata.sample_util

# Flags of the World by Vathanx:
#    http://vathanx.deviantart.com/art/World-Flag-Icons-PNG-108083900
#
# Gource:
#    http://code.google.com/p/gource
#
# GData (easy_install gdata):
#   http://code.google.com/p/gdata-python-client/
#

class LogEntry(object):
    TYPE_ADDED = "A"
    TYPE_MODIFIED = "M"
    TYPE_DELETED = "D"

    def __init__(self):
        self.date = None
        self.hour = None
        self.username = None
        self.type = LogEntry.TYPE_MODIFIED
        self.file = None
        self.colour = None
        self.visits = None

    def __str__(self):
        date_w_hour = "%s%s" % (self.date, self.hour)
        date_time = datetime.datetime.strptime(date_w_hour, "%Y%m%d%H")
        to_unix_stamp = int(time.mktime(date_time.timetuple()))

        str_log = "%s|%s|%s|%s"
        str_log = str_log % (to_unix_stamp, self.username,
                             self.type, self.file)
        if self.colour:
            str_log += "|%s" % (self.colour,)

        return str_log

def translate_to_logentry(entry):
    log_entry = LogEntry()

    for dimension in entry.dimension:
        if dimension.name == 'ga:country':
            log_entry.username = 'Flag of %s' % dimension.value

        if dimension.name == 'ga:pagePath':
            log_entry.file = dimension.value

        if dimension.name == 'ga:date':
            log_entry.date = dimension.value

        if dimension.name == 'ga:hour':
            log_entry.hour = dimension.value

    for metric in entry.metric:
        if metric.name == 'ga:visits':
            log_entry.visits = metric.value

    return log_entry

def run_main():
    app_source = 'GourceAnalyticsV1'
    ga_client = gdata.analytics.client.AnalyticsClient(source=app_source)
    
    # Uncomment this if you want to set your credentials hard coded
    #ga_client.ClientLogin('<Google Email>', '<Password>', app_source)

    try:
      gdata.sample_util.authorize_client(
          ga_client,
          service=ga_client.auth_service,
          source=app_source,
          scopes=['https://www.google.com/analytics/feeds/'])
    except gdata.client.BadAuthentication:
      exit('Invalid user credentials given.')
    except gdata.client.Error:
      exit('Login Error')

    # Change here your profile id, as well dates
    data_query = gdata.analytics.client.DataFeedQuery({
        'ids': 'ga:<your profile id>',
        'start-date': '2011-01-19',
        'end-date': '2011-02-02',
        'dimensions': 'ga:pagePath,ga:date,ga:hour,ga:country',
        'metrics': 'ga:visits',
        'sort': 'ga:date,ga:hour',
        'filters': 'ga:pagePath!@outbound;ga:pagePath!@translate;ga:pagePath!@search',
        'max-results': '500'})

    feed = ga_client.GetDataFeed(data_query)

    print '\n-------- Feed Data --------'
    print 'Feed Title          = ' + feed.title.text
    print 'Total Results Found = ' + feed.total_results.text
    print 'Start Index         = ' + feed.start_index.text
    print 'Results Returned    = ' + feed.items_per_page.text
    print 'Start Date          = ' + feed.start_date.text
    print 'End Date            = ' + feed.end_date.text
    print 'Has Sampeld Data    = ' + str(feed.HasSampledData())

    data_source = feed.data_source[0]

    print '\n-------- Data Source Data --------'
    print 'Table ID        = ' + data_source.table_id.text
    print 'Table Name      = ' + data_source.table_name.text
    print 'Web Property Id = ' + data_source.GetProperty('ga:webPropertyId').value
    print 'Profile Id      = ' + data_source.GetProperty('ga:profileId').value
    print 'Account Name    = ' + data_source.GetProperty('ga:accountName').value

    fhandle = open("custom_log.txt", "a")

    for entry in feed.entry:
        log_entry = translate_to_logentry(entry)
        for i in xrange(int(log_entry.visits)):
            fhandle.writelines(str(log_entry) + "\n")

    fhandle.close()

if __name__ == "__main__":
    run_main()