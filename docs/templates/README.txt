This folder contains additional templates e.g.
to render the special front index page.

They are not part of the translation framework so
you need to deal with that by e.g. scripting magic with multiple
static versions of the file.

The index-[locale].html files will be copied to index.html on a per locale basis
by the scripts/post_translate.sh script. So you should never place an index.html
here as it will be deleted automatically. If you want to create a new locale index
page just name it index-[locale].html and the scripts will do the rest for you.

Tim Sutton
