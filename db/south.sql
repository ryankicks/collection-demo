# get started with new system
python manage.py syncdb --settings=app.settings_my
python manage.py migrate home --settings=app.settings_my

# create new package
python manage.py schemamigration home --initial
python manage.py migrate home

# updates
python manage.py schemamigration home --auto
python manage.py migrate home

# fake migrations up to a point
python manage.py migrate home --fake 0001

# fake rollback to 0th migration
python manage.py migrate home zero --fake

# not sure what these do
python manage.py convert_to_south home --delete-ghost-migrations
python manage.py schemamigration home --auto
