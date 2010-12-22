from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _




class Course(models.Model):

        name = models.CharField(required = True)
        description = models.TextField()
        teacher = models.ForeignKey(User)
        secondary = models.ManyToMany(users.User)
        rules = dbutils.FakeModelListProperty(rules.RuleConfig, default = [])
        program_tags = models.StringListProperty(default = [])
        public_activity_creation = models.BooleanProperty(default = False)
        visible = models.IntegerProperty(default = 1)

        def ActivitiesQuery(self, keys_only = False):
                """Build query to get activities under the program."""

                return Program.ActivitiesQueryFromKey(self.key(), keys_only = keys_only)

        @staticmethod
        def ActivitiesQueryFromKey(program_key, keys_only = False):


                query = db.Query(Activity, keys_only = keys_only)
                query.ancestor(program_key)
                utils.AddFilter(query, 'deleted =', 0)

                return query

        def _GetChildrenQuery(self):
                """Overrides parent method."""

                return self.ActivitiesQuery()

        def __unicode__(self):
                return unicode(self.name)

        def ActivitySchedulesQuery(self):
                """Build query to get activity schedules under the program."""

                query = db.Query(ActivitySchedule)
                query.ancestor(self)
                utils.AddFilter(query, 'deleted =', 0)

                return query

        def RegistrationsQuery(self):
                """Build query to get registrations for activities of a program."""

                query = db.Query(UserRegistration)
                utils.AddFilter(query, 'program =', self)
                return query

        @staticmethod
        def GetSearchableProgramsQuery():
                """Query programs that can be searched."""
                program_query = Program.all()
                utils.AddFilter(program_query, 'visible =', 1)
                utils.AddFilter(program_query, 'deleted =', 0)

                return program_query


class Configuration(db.Model):


        config_key = db.StringProperty()
        config_value = db.TextProperty()
        config_binary_value = db.BlobProperty()
        last_modified = db.DateTimeProperty(auto_now = True)


class Activity(_DeletedHierarchyModel, _ModelRule):
 

        # Suppress pylint invalid inheritance from object
        # pylint: disable-msg=C6601
        class Meta:
                verbose_name = _('Activity')
                verbose_name_plural = _('Activities')

        name = db.StringProperty(required = True)
        start_time = db.DateTimeProperty()
        end_time = db.DateTimeProperty()
        rules = dbutils.FakeModelListProperty(rules.RuleConfig, default = [])
        access_point_tags = db.StringListProperty(default = [])
        reserve_rooms = db.BooleanProperty(default = True)
        visible = db.IntegerProperty(default = 1)

        def GetAccessPoints(self):
                aps = []
                for activity in self.ActivitySchedulesQuery():
                        aps.extend(activity.access_points)
                return aps

        def ActivitySchedulesQuery(self):
                """Build query to get schedules under an activity."""
                return Activity.SchedulesQueryFromActivityKey(self.key())

        def _GetChildrenQuery(self):
                """Overrides parent method."""
                return self.ActivitySchedulesQuery()

        @staticmethod
        def GetLock(activity_key):

                return utils.Lock(str(activity_key))

        @classmethod
        def SchedulesQueryFromActivityKey(cls, activity_key):
                """Build query to get the schedules under an activity given activity_key."""
                query = db.Query(ActivitySchedule)
                if isinstance(activity_key, basestring):
                        activity_key = db.Key(activity_key)
                query.ancestor(activity_key)
                utils.AddFilter(query, 'deleted =', 0)

                return query

        def RegistrationsQuery(self, keys_only = False):
                """Build query to get registrations under an activity."""
                query = db.Query(UserRegistration, keys_only = keys_only)
                return query.filter('activity =', self)

        @staticmethod
        def OrphanedActivities():
                program_set = set(db.Query(Program, keys_only = True))
                activities = db.Query(Activity)

                orphan_activities = []
                for activity in activities:
                        if activity.parent_key() not in program_set:
                                orphan_activities.append(activity)

                return orphan_activities

        def __unicode__(self):
                return unicode(self.name)

        def MaxCapacity(self):

                max_by_activity_rule = self.GetRule(rules.RuleNames.MAX_PEOPLE_ACTIVITY)
                if max_by_activity_rule:
                        return max_by_activity_rule.parameters.get('max_people', None)
                return None


class AccessPoint(_BaseModel):
  

        type = db.CategoryProperty(required = True, choices = _AccessPoint.Choices())
        uri = db.StringProperty(required = True)
        location = db.StringProperty()
        tags = db.StringListProperty()
        calendar_email = db.StringProperty(indexed = False)
        rules = dbutils.FakeModelListProperty(rules.RuleConfig)
        last_modified = db.DateTimeProperty(auto_now = True)
        deleted = db.IntegerProperty(default = 0)
        timezone = dbutils.FakeModelProperty(utils.Timezone,
                                             default = utils.Timezone('UTC'))

        def GetTimeZone(self):
                """Returns the pytz.timezone for that access point."""
                return pytz.timezone(self.timezone.name)

        @classmethod
        def GetAccessPointFromKeys(cls, keys):

                return db.get(keys)

        @classmethod
        def GetAccessPointFromUri(cls, uri):

                query = db.Query(cls).filter('uri = ', uri)
                #TODO(user): we return the first one. need to do better job here.
                #How to handle duplicates, can we store twice similar numbers like
                #321-1234 and 3211243 etc.
                return query.get()

        def Delete(self):
                """Deletes the access point."""
                self.deleted = 1
                self.put()

        def __unicode__(self):
                return unicode(self.uri)


class ActivitySchedule(_DeletedHierarchyModel):
 
        start_time = db.DateTimeProperty(required = True)
        end_time = db.DateTimeProperty(required = True)
        access_point_tags = db.StringListProperty()
        access_points = dbutils.KeyListProperty(AccessPoint)
        access_points_secondary = dbutils.KeyListProperty(AccessPoint)
        primary_instructors = db.ListProperty(users.User)
        primary_instructors_accesspoint = dbutils.KeyListProperty(AccessPoint)
        #Not indexing secondary instructors because we don't want to search them.
        secondary_instructors = db.ListProperty(users.User, indexed = False)
        calendar_edit_href = db.URLProperty()
        notes = db.TextProperty()

        def __unicode__(self):
                return unicode(self.start_time)

        def _GetChildrenQuery(self):
                """Overrides parent method."""
                return []

        @property
        def activity(self):
                return self.parent()

        @property
        def activity_key(self):
                return self.parent_key()

        @staticmethod
        def ActiveSchedulesQuery():
                """Build query to get all schedules that aren't deleted."""

                query = db.Query(ActivitySchedule)
                utils.AddFilter(query, 'deleted =', 0)

                return query

        def GetAllAccessPoints(self):
                """Returns a set of primary and secondary access points."""
                return set(self.access_points).union(self.access_points_secondary)

        def ValidateInstance(self):
    

                errors_dict = {}

                # Check access_points are valid.
                ap_list = db.get(self.access_points)
                if None in ap_list:
                        errors_dict['access_points'] = [_('Access Points not found')]

                return errors_dict

        @staticmethod
        def OrphanedActivitySchedules():
                """Get all activity schedules that have activity missing."""

                activity_set = set(db.Query(Activity, keys_only = True))

                orphan_schedules = []
                schedules = db.Query(ActivitySchedule)
                for schedule in schedules:
                        activity_key = schedule.activity_key
                        if activity_key not in activity_set:
                                orphan_schedules.append(schedule)

                return orphan_schedules

