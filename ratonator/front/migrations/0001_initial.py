# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Language'
        db.create_table('front_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('nativeName', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
        ))
        db.send_create_signal('front', ['Language'])

        # Adding model 'RateableStuff'
        db.create_table('front_rateablestuff', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('createdAt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastTouchedAt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('createdBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additions', null=True, to=orm['front.RateableUser'])),
            ('uuid', self.gf('django.db.models.fields.CharField')(default='806dfd2d-0d52-4520-aec4-c66b018d5eea', unique=True, max_length=36)),
        ))
        db.send_create_signal('front', ['RateableStuff'])

        # Adding model 'Rate'
        db.create_table('front_rate', (
            ('rateablestuff_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['front.RateableStuff'], unique=True, primary_key=True)),
            ('theRate', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True)),
            ('superseder', self.gf('django.db.models.fields.related.OneToOneField')(related_name='superseded', unique=True, null=True, to=orm['front.Rate'])),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rates', to=orm['front.RateableStuff'])),
        ))
        db.send_create_signal('front', ['Rate'])

        # Adding model 'NameableRateableStuff'
        db.create_table('front_nameablerateablestuff', (
            ('rateablestuff_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['front.RateableStuff'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('nameSlugged', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('disambiguator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ambiguousSubjects', null=True, to=orm['front.Disambiguator'])),
        ))
        db.send_create_signal('front', ['NameableRateableStuff'])

        # Adding unique constraint on 'NameableRateableStuff', fields ['language', 'name']
        db.create_unique('front_nameablerateablestuff', ['language', 'name'])

        # Adding unique constraint on 'NameableRateableStuff', fields ['language', 'nameSlugged']
        db.create_unique('front_nameablerateablestuff', ['language', 'nameSlugged'])

        # Adding model 'Aspect'
        db.create_table('front_aspect', (
            ('nameablerateablestuff_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['front.NameableRateableStuff'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('front', ['Aspect'])

        # Adding M2M table for field subjects on 'Aspect'
        db.create_table('front_aspect_subjects', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('aspect', models.ForeignKey(orm['front.aspect'], null=False)),
            ('classifiablerateablestuff', models.ForeignKey(orm['front.classifiablerateablestuff'], null=False))
        ))
        db.create_unique('front_aspect_subjects', ['aspect_id', 'classifiablerateablestuff_id'])

        # Adding model 'AspectRate'
        db.create_table('front_aspectrate', (
            ('rate_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['front.Rate'], unique=True, primary_key=True)),
            ('aspect', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['front.Aspect'])),
            ('baseRate', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ratingAspects', to=orm['front.Rate'])),
        ))
        db.send_create_signal('front', ['AspectRate'])

        # Adding model 'ClassifiableRateableStuff'
        db.create_table('front_classifiablerateablestuff', (
            ('nameablerateablestuff_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['front.NameableRateableStuff'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('front', ['ClassifiableRateableStuff'])

        # Adding model 'Classification'
        db.create_table('front_classification', (
            ('rateablestuff_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['front.RateableStuff'], unique=True, primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='categories', to=orm['front.ClassifiableRateableStuff'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subjects', to=orm['front.ClassifiableRateableStuff'])),
        ))
        db.send_create_signal('front', ['Classification'])

        # Adding unique constraint on 'Classification', fields ['subject', 'category']
        db.create_unique('front_classification', ['subject_id', 'category_id'])

        # Adding model 'Definition'
        db.create_table('front_definition', (
            ('rateablestuff_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['front.RateableStuff'], unique=True, primary_key=True)),
            ('theDefinition', self.gf('django.db.models.fields.TextField')()),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='definitions', to=orm['front.ClassifiableRateableStuff'])),
        ))
        db.send_create_signal('front', ['Definition'])

        # Adding model 'Disambiguator'
        db.create_table('front_disambiguator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('commonTerm', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('front', ['Disambiguator'])

        # Adding unique constraint on 'Disambiguator', fields ['commonTerm', 'language']
        db.create_unique('front_disambiguator', ['commonTerm', 'language'])

        # Adding model 'Kill'
        db.create_table('front_kill', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('killedAt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('killer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='kills', to=orm['front.RateableUser'])),
            ('killed', self.gf('django.db.models.fields.related.ForeignKey')(related_name='killers', to=orm['front.RateableUser'])),
        ))
        db.send_create_signal('front', ['Kill'])

        # Adding model 'RateableUser'
        db.create_table('front_rateableuser', (
            ('rateablestuff_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['front.RateableStuff'], unique=True, primary_key=True)),
            ('defaultLanguage', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('validatedAt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('lastLoggedOnAt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('front', ['RateableUser'])

        # Adding model 'UserBio'
        db.create_table('front_userbio', (
            ('rateablestuff_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['front.RateableStuff'], unique=True, primary_key=True)),
            ('theBio', self.gf('django.db.models.fields.TextField')()),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='bio', unique=True, to=orm['front.RateableUser'])),
        ))
        db.send_create_signal('front', ['UserBio'])

        # Adding model 'UserValidation'
        db.create_table('front_uservalidation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(default='f66c8d00-b611-4f23-9d92-725e682f576b', unique=True, max_length=36)),
            ('requestedAt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expiresAt', self.gf('django.db.models.fields.DateTimeField')()),
            ('validatedAt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['front.RateableUser'])),
        ))
        db.send_create_signal('front', ['UserValidation'])

        # Adding model 'PasswordResetRequest'
        db.create_table('front_passwordresetrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(default='ea191e9c-82fd-4978-a62d-259147e202ec', unique=True, max_length=36)),
            ('requestedAt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expiresAt', self.gf('django.db.models.fields.DateTimeField')()),
            ('validatedAt', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['front.RateableUser'])),
        ))
        db.send_create_signal('front', ['PasswordResetRequest'])


    def backwards(self, orm):
        # Removing unique constraint on 'Disambiguator', fields ['commonTerm', 'language']
        db.delete_unique('front_disambiguator', ['commonTerm', 'language'])

        # Removing unique constraint on 'Classification', fields ['subject', 'category']
        db.delete_unique('front_classification', ['subject_id', 'category_id'])

        # Removing unique constraint on 'NameableRateableStuff', fields ['language', 'nameSlugged']
        db.delete_unique('front_nameablerateablestuff', ['language', 'nameSlugged'])

        # Removing unique constraint on 'NameableRateableStuff', fields ['language', 'name']
        db.delete_unique('front_nameablerateablestuff', ['language', 'name'])

        # Deleting model 'Language'
        db.delete_table('front_language')

        # Deleting model 'RateableStuff'
        db.delete_table('front_rateablestuff')

        # Deleting model 'Rate'
        db.delete_table('front_rate')

        # Deleting model 'NameableRateableStuff'
        db.delete_table('front_nameablerateablestuff')

        # Deleting model 'Aspect'
        db.delete_table('front_aspect')

        # Removing M2M table for field subjects on 'Aspect'
        db.delete_table('front_aspect_subjects')

        # Deleting model 'AspectRate'
        db.delete_table('front_aspectrate')

        # Deleting model 'ClassifiableRateableStuff'
        db.delete_table('front_classifiablerateablestuff')

        # Deleting model 'Classification'
        db.delete_table('front_classification')

        # Deleting model 'Definition'
        db.delete_table('front_definition')

        # Deleting model 'Disambiguator'
        db.delete_table('front_disambiguator')

        # Deleting model 'Kill'
        db.delete_table('front_kill')

        # Deleting model 'RateableUser'
        db.delete_table('front_rateableuser')

        # Deleting model 'UserBio'
        db.delete_table('front_userbio')

        # Deleting model 'UserValidation'
        db.delete_table('front_uservalidation')

        # Deleting model 'PasswordResetRequest'
        db.delete_table('front_passwordresetrequest')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'front.aspect': {
            'Meta': {'object_name': 'Aspect', '_ormbases': ['front.NameableRateableStuff']},
            'nameablerateablestuff_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['front.NameableRateableStuff']", 'unique': 'True', 'primary_key': 'True'}),
            'subjects': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'aspects'", 'symmetrical': 'False', 'to': "orm['front.ClassifiableRateableStuff']"})
        },
        'front.aspectrate': {
            'Meta': {'object_name': 'AspectRate', '_ormbases': ['front.Rate']},
            'aspect': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['front.Aspect']"}),
            'baseRate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratingAspects'", 'to': "orm['front.Rate']"}),
            'rate_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['front.Rate']", 'unique': 'True', 'primary_key': 'True'})
        },
        'front.classifiablerateablestuff': {
            'Meta': {'object_name': 'ClassifiableRateableStuff', '_ormbases': ['front.NameableRateableStuff']},
            'nameablerateablestuff_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['front.NameableRateableStuff']", 'unique': 'True', 'primary_key': 'True'})
        },
        'front.classification': {
            'Meta': {'unique_together': "(('subject', 'category'),)", 'object_name': 'Classification', '_ormbases': ['front.RateableStuff']},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subjects'", 'to': "orm['front.ClassifiableRateableStuff']"}),
            'rateablestuff_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['front.RateableStuff']", 'unique': 'True', 'primary_key': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categories'", 'to': "orm['front.ClassifiableRateableStuff']"})
        },
        'front.definition': {
            'Meta': {'object_name': 'Definition', '_ormbases': ['front.RateableStuff']},
            'rateablestuff_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['front.RateableStuff']", 'unique': 'True', 'primary_key': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'definitions'", 'to': "orm['front.ClassifiableRateableStuff']"}),
            'theDefinition': ('django.db.models.fields.TextField', [], {})
        },
        'front.disambiguator': {
            'Meta': {'unique_together': "(('commonTerm', 'language'),)", 'object_name': 'Disambiguator'},
            'commonTerm': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'front.kill': {
            'Meta': {'object_name': 'Kill'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'killed': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'killers'", 'to': "orm['front.RateableUser']"}),
            'killedAt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'killer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'kills'", 'to': "orm['front.RateableUser']"})
        },
        'front.language': {
            'Meta': {'object_name': 'Language'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'nativeName': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'front.nameablerateablestuff': {
            'Meta': {'unique_together': "(('language', 'name'), ('language', 'nameSlugged'))", 'object_name': 'NameableRateableStuff', '_ormbases': ['front.RateableStuff']},
            'disambiguator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ambiguousSubjects'", 'null': 'True', 'to': "orm['front.Disambiguator']"}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nameSlugged': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'rateablestuff_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['front.RateableStuff']", 'unique': 'True', 'primary_key': 'True'})
        },
        'front.passwordresetrequest': {
            'Meta': {'object_name': 'PasswordResetRequest'},
            'expiresAt': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requestedAt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['front.RateableUser']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'e40b94bb-dec7-4df3-9b5c-a4714437d079'", 'unique': 'True', 'max_length': '36'}),
            'validatedAt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'front.rate': {
            'Meta': {'object_name': 'Rate', '_ormbases': ['front.RateableStuff']},
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'rateablestuff_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['front.RateableStuff']", 'unique': 'True', 'primary_key': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rates'", 'to': "orm['front.RateableStuff']"}),
            'superseder': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'superseded'", 'unique': 'True', 'null': 'True', 'to': "orm['front.Rate']"}),
            'theRate': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'front.rateablestuff': {
            'Meta': {'object_name': 'RateableStuff'},
            'createdAt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'createdBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'additions'", 'null': 'True', 'to': "orm['front.RateableUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastTouchedAt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'2cd8c35d-e752-4aaa-82f8-efc18bd87842'", 'unique': 'True', 'max_length': '36'})
        },
        'front.rateableuser': {
            'Meta': {'object_name': 'RateableUser', '_ormbases': ['front.RateableStuff']},
            'defaultLanguage': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'lastLoggedOnAt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'rateablestuff_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['front.RateableStuff']", 'unique': 'True', 'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'validatedAt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'front.userbio': {
            'Meta': {'object_name': 'UserBio', '_ormbases': ['front.RateableStuff']},
            'rateablestuff_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['front.RateableStuff']", 'unique': 'True', 'primary_key': 'True'}),
            'theBio': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'bio'", 'unique': 'True', 'to': "orm['front.RateableUser']"})
        },
        'front.uservalidation': {
            'Meta': {'object_name': 'UserValidation'},
            'expiresAt': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requestedAt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['front.RateableUser']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'7f724899-c654-44fa-89dd-781a7551c9e9'", 'unique': 'True', 'max_length': '36'}),
            'validatedAt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        }
    }

    complete_apps = ['front']