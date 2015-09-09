# Derived from the dropbox-index project found here:
# http://code.google.com/p/kosciak-misc/wiki/DropboxIndex

import os, time, ctypes, argparse

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

FILE_TYPES = {
    ('gif', 'jpg', 'jpeg', 'png', 'bmp', 'tif', 'tiff', 'raw', 'img', 'ico', ): 'image',
    ('avi', 'ram', 'mpg', 'mpeg', 'mov', 'asf', 'wmv', 'asx', 'ogm', 'vob', '3gp', ): 'video',
    ('mp3', 'ogg', 'mpc', 'wav', 'wave', 'flac', 'shn', 'ape', 'mid', 'midi', 'wma', 'rm', 'aac', 'mka', ): 'music',
    ('tar', 'bz2', 'gz', 'arj', 'rar', 'zip', '7z', ): 'archive',
    ('deb', 'rpm', 'pkg', 'jar', 'war', 'ear', ): 'package', 
    ('pdf', ): 'pdf',
    ('txt', ): 'txt',
    ('html', 'htm', 'xml', 'css', 'rss', 'yaml', 'php', 'php3', 'php4', 'php5', ): 'markup',
    ('js', 'py', 'pl', 'java', 'c', 'h', 'cpp', 'hpp', 'sql', ): 'code',
    ('ttf', 'otf', 'fnt', ): 'font',
    ('doc', 'rtf', 'odt', 'abw', 'docx', 'sxw', ): 'document',
    ('xls', 'ods', 'csv', 'sdc', 'xlsx', ): 'spreadsheet',
    ('ppt', 'odp', 'pptx', ): 'presentation', 
    ('exe', 'msi', 'bin', 'dmg', ): 'application',
    ('xpi', ): 'plugin',
    ('iso', 'nrg', ): 'iso',
}

FILES_URL = 'http://dl.dropbox.com/u/69843/dropbox-index'

ICONS = (
    FILES_URL + '/icons/back.png',
    FILES_URL + '/icons/folder.png',
    FILES_URL + '/icons/file.png',
    FILES_URL + '/icons/image.png',
    FILES_URL + '/icons/video.png',
    FILES_URL + '/icons/music.png',
    FILES_URL + '/icons/archive.png',
    FILES_URL + '/icons/package.png',
    FILES_URL + '/icons/pdf.png',
    FILES_URL + '/icons/txt.png',
    FILES_URL + '/icons/markup.png',
    FILES_URL + '/icons/code.png',
    FILES_URL + '/icons/font.png',
    FILES_URL + '/icons/document.png',
    FILES_URL + '/icons/spreadsheet.png',
    FILES_URL + '/icons/presentation.png',
    FILES_URL + '/icons/application.png',
    FILES_URL + '/icons/plugin.png',
    FILES_URL + '/icons/iso.png',
)

HTML_STYLE = '''
    <style>
        body { font-family: Verdana, sans-serif; font-size: 12px;}
        a { text-decoration: none; color: #00A; }
        a:hover { text-decoration: underline; }
        #dropbox-index-header { padding: 0; margin: 0.5em auto 0.5em 1em; }
        table#dropbox-index-list { text-align: center; margin: 0 auto 0 1.5em; border-collapse: collapse; }
        #dropbox-index-list thead { border-bottom: 1px solid #555; }
        #dropbox-index-list th:hover { cursor: pointer; cursor: hand; background-color: #EEE; }
        #direction { border: 0; vertical-align: bottom; margin: 0 0.5em;}
        #dropbox-index-list tbody { border-bottom: 1px solid #555;}
        #dropbox-index-list tr, th { line-height: 1.7em; min-height: 25px; }
        #dropbox-index-list tbody tr:hover { background-color: #EEE; }
        .name { text-align: left; width: 35em; }
        .name a, thead .name { padding-left: 22px; }
        .name a { display: block; }
        .size { text-align: right; width: 7em; padding-right: 1em;}
        .date { text-align: right; width: 15em; padding-right: 1em;}
        #dropbox-index-dir-info { margin: 1em auto 0.5em 2em; }
        #dropbox-index-footer { margin: 1em auto 0.5em 2em; font-size: smaller;}
        /* Icons */
        .dir, .back, .file { background-repeat: no-repeat; background-position: 2px 4px;}
        .back { background-image: url('%s'); }
        .dir { background-image: url('%s'); }
        .file { background-image: url('%s'); }
        .image { background-image: url('%s'); }
        .video { background-image: url('%s'); }
        .music { background-image: url('%s'); }
        .archive { background-image: url('%s'); }
        .package { background-image: url('%s'); }
        .pdf { background-image: url('%s'); }
        .txt { background-image: url('%s'); }
        .markup { background-image: url('%s'); }
        .code { background-image: url('%s'); }
        .font { background-image: url('%s'); }
        .document { background-image: url('%s'); }
        .spreadsheet { background-image: url('%s'); }
        .presentation { background-image: url('%s'); }
        .application { background-image: url('%s'); }
        .plugin { background-image: url('%s'); }
        .iso { background-image: url('%s'); }
    </style>
''' % ICONS

HTML_JAVASCRIPT = '''
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
    <script>
        function sort() {
            column = $(this).attr("class").split(' ')[0];
            $("#direction").remove();
            if ($(this).hasClass("desc")) {
                $("#dropbox-index-list thead tr th").each(function(i) { $(this).removeClass("asc").removeClass("desc") });
                $(this).addClass("asc");
                reverse = -1;
            } else {
                $("#dropbox-index-list thead tr th").each(function(i) { $(this).removeClass("asc").removeClass("desc") });
                $(this).addClass("desc");
                reverse = 1;
            }
            if (column == "name") {
                $(this).append('<img src="%s/icons/'+((reverse == 1) ? 'desc' : 'asc')+'.png" id="direction" />');
            } else {
                $(this).prepend('<img src="%s/icons/'+((reverse == 1) ? 'desc' : 'asc')+'.png" id="direction" />');
            }
            rows = $("#dropbox-index-list tbody tr").detach()
            rows.sort(function(a, b) {
                result = $(a).data('type') - $(b).data('type')
                if (result != 0) { return result }
                
                return (($(a).data(column) < $(b).data(column)) - ($(a).data(column) > $(b).data(column))) * reverse
                
            });
            $("#dropbox-index-list tbody").append(rows);
        }
        
        function prepare() {
            $("#dropbox-index-list tbody tr").each(function(i) {
                if ($(this).children(".name").hasClass("back")) {
                    $(this).data('type', 1);
                } else if ($(this).children(".name").hasClass("dir")) {
                    $(this).data('type', 2);
                } else {
                    $(this).data('type', 3);
                }
                $(this).data('name', $(this).children(".name").text().toLowerCase());
                $(this).data('size', parseInt($(this).children(".size").attr("sort")));
                $(this).data('date', parseInt($(this).children(".date").attr("sort")));
            });
            
            $("#dropbox-index-list thead tr th").each(function(i) {
                $(this).bind('click', sort);
            });
        }

        $(document).ready(function(){
            prepare();
        });
    </script>
''' % (FILES_URL, FILES_URL)

FAVICON = '<link rel="shortcut icon" href="%s/icons/favicon.ico"/>' % FILES_URL

HTML_START = '''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/> 
            <title>%s</title>
            %s
            %s
            %s
''' % ('%s', FAVICON, HTML_STYLE, HTML_JAVASCRIPT)

HTML_NOINDEX = '<meta name="robots" content="index, nofollow">'

HTML_HEAD_TO_BODY = '''
    </head>
    <body>
'''

HTML_HEADER = '<h1 id="dropbox-index-header">%s</h1>'

HTML_TABLE_START = '''
    <table id="dropbox-index-list">
        <thead>
            <tr>
                <th class="name">Name</th>
                <th class="size">Size</th>
                <th class="date">Last Modified</th>
            </tr>
        </thead>
        <tbody>
'''

HTML_TABLE_END = '''
        </tbody>
    </table>
    <div id="dropbox-index-footer">
        Generated on <strong>%s</strong>
    </div>
'''

HTML_BACK = '''
    <tr>
        <td class="name back">
            <a href="../index.html">..</a>
        </td>
        <td class="size">
            &nbsp;
        </td>
        <td class="date">
            &nbsp;
        </td>
    </tr>
'''

HTML_DIR = '''
    <tr>
        <td class="name dir">
            <a href="%(name)s/index.html">%(name)s</a>
        </td>
        <td class="size">
            &nbsp;
        </td>
        <td class="date" sort="%(time_sort)s">
            %(time)s
        </td>
    </tr>
'''

HTML_FILE = '''
    <tr>
        <td class="name file%(type)s">
            <a href="%(name)s">%(name)s</a>
        </td>
        <td class="size" sort="%(size_sort)s">
            %(size)s
        </td>
        <td class="date" sort="%(time_sort)s">
            %(time)s
        </td>
    </tr>
'''

HTML_END = '''
        </body>
    </html>
'''

def from_command_line():
    parser = argparse.ArgumentParser(
        description = 'Creates an index.html file which lists the contents of the directory',
        epilog = 'This tool will overwrite any existing index.html file(s)'
    )

    parser.add_argument(
        '-R', '-r', '--recursive',
        action = 'store_true',
        default = False,
        help = 'Include subdirectories [default: %(default)s]'
    )

    parser.add_argument(
        '-S', '-s', '--searchable',
        action = 'store_true',
        default = False,
        help = 'Allow created page to be listed by search engines [default: %(default)s]'
    )

    parser.add_argument(
        'directory',
        help = 'The directory to process [Required]'
    )

    args = parser.parse_args()

    build_index(args.directory, args.recursive, args.searchable)

def build_index(path, recursive = False, searchable = False, parent = None):
    if not os.path.isdir(path):
        print('ERROR: Directory {0} does not exist'.format(path))
        return False

    contents = [os.path.join(path, file) for file in os.listdir(path) if file != 'index.html']
    contents = [file for file in contents if not is_hidden(file)]

    files = [file for file in contents if os.path.isfile(file)]
    files.sort(key = str.lower)

    if recursive:
        dirs = [file for file in contents if os.path.isdir(file)]
        dirs.sort(key = str.lower)
    else:
        dirs = []

    build_html(path, parent, dirs, files, searchable)

    print('Created index.html for ' + os.path.realpath(path))

    for dir in dirs:
        build_index(dir, recursive, searchable, path)

    return True

def is_hidden(filepath):
    filename = os.path.basename(os.path.abspath(filepath))
    return filename.startswith('.') or has_hidden_attribute(filepath)

def has_hidden_attribute(filepath):
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
        if attrs == -1:
            return False

        return bool(attrs & 2)

    except (AttributeError):
        return False

def build_html(path, parent, dirs, files, searchable):
    here = os.path.basename(os.path.realpath(path))
    index_file = open(os.path.join(path, 'index.html'), 'w')

    index_file.write(HTML_START % here)
    if not searchable:
        index_file.write(HTML_NOINDEX)

    index_file.write(HTML_HEAD_TO_BODY)

    index_file.write(HTML_HEADER % here)

    index_file.write(HTML_TABLE_START)

    if parent:
        index_file.write(HTML_BACK)

    for dir in dirs:
        dir_info = {}
        dir_info['name'] = os.path.basename(dir)
        dir_info['time'] = time.strftime(DATE_FORMAT, time.localtime(os.path.getmtime(dir)))
        dir_info['time_sort'] = os.path.getmtime(dir)
        index_file.write(HTML_DIR % dir_info)

    for file in files:
        file_info = {}
        file_info['name'] = os.path.basename(file)
        file_info['type'] = get_filetype(os.path.basename(file))
        file_info['size'] = get_size(file)
        file_info['size_sort'] = os.path.getsize(file)
        file_info['time'] = time.strftime(DATE_FORMAT, time.localtime(os.path.getmtime(file)))
        file_info['time_sort'] = os.path.getmtime(file)
        index_file.write(HTML_FILE % file_info)

    index_file.write(HTML_TABLE_END % time.strftime(DATE_FORMAT, time.localtime()))
    index_file.write(HTML_END)

def get_filetype(file_name):
    ext = file_name.rsplit('.', 1)[-1].lower()
    for keys, value in FILE_TYPES.items():
        if ext in keys:
            return ' ' + value

    return ''

def get_size(file):
    size = os.path.getsize(file)

    if size < 1000:
        return '%s bytes' % size

    kilo = size / 1024
    if kilo < 1000:
        return '%s KB' % round(kilo, 1)

    mega = kilo / 1024
    if mega < 1000:
        return '%s MB' % round(mega, 1)

    giga = mega / 1024
    return '%s GB' % round(giga, 1)

if __name__ == '__main__':
    from_command_line()
