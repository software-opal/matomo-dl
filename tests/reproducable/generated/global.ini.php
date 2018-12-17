; <?php exit; ?> DO NOT REMOVE THIS LINE

[database]
host =
username =
password =
dbname =
tables_prefix =
port = 3306
adapter = PDO\MYSQL
type = InnoDB
schema = Mysql
enable_ssl = 0
ssl_ca =
ssl_cert =
ssl_key =
ssl_ca_path =
ssl_cipher =
ssl_no_verify =
charset = utf8

[database_tests]
host = localhost
username = "@USERNAME@"
password =
dbname = piwik_tests
tables_prefix = piwiktests_
port = 3306
adapter = PDO\MYSQL
type = InnoDB
schema = Mysql
charset = utf8
enable_ssl = 0
ssl_ca =
ssl_cert =
ssl_key =
ssl_ca_path =
ssl_cipher =
ssl_no_verify = 1

[tests]
http_host = localhost
remote_addr = "127.0.0.1"
request_uri = "@REQUEST_URI@"
port =
enable_logging = 0
aws_accesskey = ""
aws_secret = ""
aws_keyname = ""
aws_pem_file = "<path to pem file>"
aws_securitygroups[] = default
aws_region = us-east-1
aws_ami = ami-ac24bac4
aws_instance_type = c3.large

[log]
log_writers[] = screen
log_level = WARN
logger_file_path = tmp/logs/piwik.log

[Cache]
backend = chained

[ChainedCache]
backends[] = array
backends[] = file

[RedisCache]
host = "127.0.0.1"
port = 6379
unix_socket = ""
timeout = 0.0
password = ""
database = 14

[Debug]
always_archive_data_period = 0
always_archive_data_day = 0
always_archive_data_range = 0
enable_sql_profiler = 0
tracker_always_new_visitor = 0
log_sql_queries = 0
archiving_profile = 0
archive_profiling_log =

[DebugTests]
enable_load_standalone_plugins_during_tests = 0

[Development]
enabled = 0
disable_merged_assets = 0

[General]
enable_processing_unique_visitors_day = 1
enable_processing_unique_visitors_week = 1
enable_processing_unique_visitors_month = 1
enable_processing_unique_visitors_year = 0
enable_processing_unique_visitors_range = 0
enable_processing_unique_visitors_multiple_sites = 0
enabled_periods_UI = day,week,month,year,range
enabled_periods_API = day,week,month,year,range
enable_segments_subquery_cache = 0
segments_subquery_cache_limit = 100000
segments_subquery_cache_ttl = 3600
maintenance_mode = 0
release_channel = latest_stable
action_url_category_delimiter = "/"
action_title_category_delimiter = "/"
action_category_level_limit = 10
autocomplete_min_sites = 5
site_selector_max_sites = 15
show_multisites_sparklines = 1
all_websites_website_per_page = 50
anonymous_user_enable_use_segments_API = 1
browser_archiving_disabled_enforce = 0
currencies[BTC] = Bitcoin
enable_create_realtime_segments = 1
enable_segment_suggested_values = 1
adding_segment_requires_access = view
allow_adding_segments_for_all_websites = 1
process_new_segments_from = beginning_of_time
action_default_name = index
default_language = en
datatable_default_limit = 10
datatable_row_limits = "5,10,25,50,100,250,500,-1"
API_datatable_default_limit = 100
datatable_export_range_as_day = rss
default_day = yesterday
default_period = day
time_before_today_archive_considered_outdated = 150
time_before_week_archive_considered_outdated = -1
time_before_month_archive_considered_outdated = -1
time_before_year_archive_considered_outdated = -1
time_before_range_archive_considered_outdated = -1
enable_browser_archiving_triggering = 1
archiving_range_force_on_browser_request = 1
enable_sql_optimize_queries = 1
purge_date_range_archives_after_X_days = 1
minimum_mysql_version = 4.1
minimum_pgsql_version = 8.3
minimum_memory_limit = 128
minimum_memory_limit_when_archiving = 768
disable_checks_usernames_attributes = 0
hash_algorithm = whirlpool
session_save_handler = files
force_ssl = 0
login_cookie_name = piwik_auth
login_cookie_expire = 1209600
login_cookie_path =
login_password_recovery_email_address = password-recovery@{DOMAIN}
login_password_recovery_email_name = Matomo
login_password_recovery_replyto_email_address = no-reply@{DOMAIN}
login_password_recovery_replyto_email_name = No-reply
login_whitelist_apply_to_reporting_api_requests = 1
enable_framed_pages = 0
enable_framed_settings = 0
language_cookie_name = piwik_lang
noreply_email_address = noreply@{DOMAIN}
noreply_email_name = ""
feedback_email_address = feedback@matomo.org
scheduled_reports_replyto_is_user_email_and_alias = 0
scheduled_reports_truncate = 23
datatable_archiving_maximum_rows_referrers = 1000
datatable_archiving_maximum_rows_subtable_referrers = 50
datatable_archiving_maximum_rows_userid_users = 50000
datatable_archiving_maximum_rows_custom_variables = 1000
datatable_archiving_maximum_rows_subtable_custom_variables = 1000
datatable_archiving_maximum_rows_actions = 500
datatable_archiving_maximum_rows_subtable_actions = 100
datatable_archiving_maximum_rows_events = 500
datatable_archiving_maximum_rows_subtable_events = 500
datatable_archiving_maximum_rows_standard = 500
archiving_ranking_query_row_limit = 50000
visitor_log_maximum_actions_per_visit = 500
live_widget_refresh_after_seconds = 5
live_widget_visitor_count_last_minutes = 3
live_visitor_profile_max_visits_to_aggregate = 100
multisites_refresh_after_seconds = 300
show_update_notification_to_superusers_only = 0
assume_secure_protocol = 0
multi_server_environment = 0
proxy_uri_header = 0
enable_trusted_host_check = 1
api_service_url = http://api.matomo.org
graphs_default_period_to_plot_when_period_range = day
graphs_show_evolution_within_selected_period = 0
overlay_following_pages_limit = 300
overlay_disable_framed_mode = 0
enable_custom_logo_check = 1
absolute_chroot_path =
tmp_path = "/tmp"
enable_load_data_infile = 1
enable_plugins_admin = 1
enable_plugin_upload = 0
enable_installer = 1
enable_geolocation_admin = 1
enable_delete_old_data_settings_admin = 1
enable_general_settings_admin = 1
enable_internet_features = 1
enable_auto_update = 1
enable_update_communication = 1
always_load_commands_from_plugin =
pivot_by_filter_enable_fetch_by_segment = 0
pivot_by_filter_default_column_limit = 10
piwik_professional_support_ads_enabled = 1
num_days_before_tracking_code_reminder = 5

[Tracker]
enable_fingerprinting_across_websites = 0
use_third_party_id_cookie = 0
debug = 0
debug_on_demand = 0
trust_visitors_cookies = 0
cookie_name = "_pk_uid"
cookie_expire = 33955200
cookie_path =
cookie_domain =
record_statistics = 1
visit_standard_length = 1800
window_look_back_for_visitor = 0
default_time_one_page_visit = 0
url_query_parameter_to_exclude_from_url = gclid,fb_xd_fragment,fb_comment_id,phpsessid,jsessionid,sessionid,aspsessionid,doing_wp_cron,sid,pk_vid
enable_language_to_country_guess = 1
scheduled_tasks_min_interval = 3600
ignore_visits_cookie_name = piwik_ignore
campaign_var_name = pk_cpn,pk_campaign,piwik_campaign,utm_campaign,utm_source,utm_medium
campaign_keyword_var_name = pk_kwd,pk_keyword,piwik_kwd,utm_term
create_new_visit_when_campaign_changes = 1
create_new_visit_when_website_referrer_changes = 0
create_new_visit_after_midnight = 1
page_maximum_length = 1024
tracker_cache_file_ttl = 300
bulk_requests_require_authentication = 0
bulk_requests_use_transaction = 1
tracking_requests_require_authentication = 1
tracking_requests_require_authentication_when_custom_timestamp_newer_than = 86400

[Segments]

[Deletelogs]
delete_logs_enable = 0
delete_logs_schedule_lowest_interval = 7
delete_logs_older_than = 180
delete_logs_max_rows_per_query = 100000
enable_auto_database_size_estimate = 1
enable_database_size_estimate = 1

[Deletereports]
delete_reports_enable = 0
delete_reports_older_than = 12
delete_reports_keep_basic_metrics = 1
delete_reports_keep_day_reports = 0
delete_reports_keep_week_reports = 0
delete_reports_keep_month_reports = 1
delete_reports_keep_year_reports = 1
delete_reports_keep_range_reports = 0
delete_reports_keep_segment_reports = 0

[mail]
defaultHostnameIfEmpty = defaultHostnameIfEmpty.example.org
transport =
port =
host =
type =
username =
password =
encryption =

[proxy]
type = BASIC
host =
port =
username =
password =

[Plugins]
Plugins[] = CorePluginsAdmin
Plugins[] = CoreAdminHome
Plugins[] = CoreHome
Plugins[] = WebsiteMeasurable
Plugins[] = IntranetMeasurable
Plugins[] = Diagnostics
Plugins[] = CoreVisualizations
Plugins[] = Proxy
Plugins[] = API
Plugins[] = Widgetize
Plugins[] = Transitions
Plugins[] = LanguagesManager
Plugins[] = Actions
Plugins[] = Dashboard
Plugins[] = MultiSites
Plugins[] = Referrers
Plugins[] = UserLanguage
Plugins[] = DevicesDetection
Plugins[] = Goals
Plugins[] = Ecommerce
Plugins[] = SEO
Plugins[] = Events
Plugins[] = UserCountry
Plugins[] = GeoIp2
Plugins[] = VisitsSummary
Plugins[] = VisitFrequency
Plugins[] = VisitTime
Plugins[] = VisitorInterest
Plugins[] = RssWidget
Plugins[] = Feedback
Plugins[] = Monolog
Plugins[] = Login
Plugins[] = UsersManager
Plugins[] = SitesManager
Plugins[] = Installation
Plugins[] = CoreUpdater
Plugins[] = CoreConsole
Plugins[] = ScheduledReports
Plugins[] = UserCountryMap
Plugins[] = Live
Plugins[] = CustomVariables
Plugins[] = PrivacyManager
Plugins[] = ImageGraph
Plugins[] = Annotations
Plugins[] = MobileMessaging
Plugins[] = Overlay
Plugins[] = SegmentEditor
Plugins[] = Insights
Plugins[] = Morpheus
Plugins[] = Contents
Plugins[] = BulkTracking
Plugins[] = Resolution
Plugins[] = DevicePlugins
Plugins[] = Heartbeat
Plugins[] = Intl
Plugins[] = Marketplace
Plugins[] = ProfessionalServices
Plugins[] = UserId
Plugins[] = CustomPiwikJs

[PluginsInstalled]
PluginsInstalled[] = Diagnostics
PluginsInstalled[] = Login
PluginsInstalled[] = CoreAdminHome
PluginsInstalled[] = UsersManager
PluginsInstalled[] = SitesManager
PluginsInstalled[] = Installation
PluginsInstalled[] = Monolog
PluginsInstalled[] = Intl
PluginsInstalled[] = CorePluginsAdmin
PluginsInstalled[] = CoreHome
PluginsInstalled[] = CoreVisualizations
PluginsInstalled[] = API
PluginsInstalled[] = Widgetize
PluginsInstalled[] = Transitions
PluginsInstalled[] = LanguagesManager
PluginsInstalled[] = Actions
PluginsInstalled[] = Dashboard
PluginsInstalled[] = MultiSites
PluginsInstalled[] = Referrers
PluginsInstalled[] = UserLanguage
PluginsInstalled[] = DevicesDetection
PluginsInstalled[] = Goals
PluginsInstalled[] = SEO
PluginsInstalled[] = Events
PluginsInstalled[] = UserCountry
PluginsInstalled[] = GeoIp2
PluginsInstalled[] = VisitsSummary
PluginsInstalled[] = VisitFrequency
PluginsInstalled[] = VisitTime
PluginsInstalled[] = VisitorInterest
PluginsInstalled[] = Feedback
PluginsInstalled[] = CoreUpdater
PluginsInstalled[] = CoreConsole
PluginsInstalled[] = ScheduledReports
PluginsInstalled[] = UserCountryMap
PluginsInstalled[] = Live
PluginsInstalled[] = CustomVariables
PluginsInstalled[] = PrivacyManager
PluginsInstalled[] = ImageGraph
PluginsInstalled[] = Annotations
PluginsInstalled[] = MobileMessaging
PluginsInstalled[] = Overlay
PluginsInstalled[] = SegmentEditor
PluginsInstalled[] = Insights
PluginsInstalled[] = Contents
PluginsInstalled[] = Resolution
PluginsInstalled[] = DevicePlugins
PluginsInstalled[] = Marketplace
PluginsInstalled[] = UserId
PluginsInstalled[] = CustomPiwikJs

[APISettings]
SDK_batch_size = 10
SDK_interval_value = 30
