# Derived from the dropbox-index project found here:
# http://code.google.com/p/kosciak-misc/wiki/DropboxIndex

import os, time, ctypes, argparse
from string import Template

class HtmlIndex:
    format_date = lambda self, date: time.strftime('%Y-%m-%d %H:%M:%S', date)

    file_types = {
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

    image_base_url = 'http://dl.dropbox.com/u/69843/dropbox-index/icons/'

    page_template = Template(
        '<!DOCTYPE HTML>'
        '<html lang="en">'
            '<head>'
                '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'
                '<meta name="robots" content="${robots}">'
                '<title>${title}</title>'
                '<link rel="shortcut icon" href="${base_url}favicon.ico"/>'
                '<style>'
                    'body { font-family: Verdana, sans-serif; font-size: 12px;}'
                    'a { text-decoration: none; color: #00A; }'
                    'a:hover { text-decoration: underline; }'
                    '#html-index-header { padding: 0; margin: 0.5em auto 0.5em 1em; }'
                    'table#html-index-list { text-align: center; margin: 0 auto 0 1.5em; border-collapse: collapse; }'
                    '#html-index-list thead { border-bottom: 1px solid #555; }'
                    '#html-index-list th:hover { cursor: pointer; cursor: hand; background-color: #EEE; }'
                    '#direction { border: 0; vertical-align: bottom; margin: 0 0.5em;}'
                    '#html-index-list tbody { border-bottom: 1px solid #555;}'
                    '#html-index-list tr, th { line-height: 1.7em; min-height: 25px; }'
                    '#html-index-list tbody tr:hover { background-color: #EEE; }'
                    '.name { text-align: left; width: 35em; }'
                    '.name a, thead .name { padding-left: 22px; }'
                    '.name a { display: block; }'
                    '.size { text-align: right; width: 7em; padding-right: 1em;}'
                    '.date { text-align: right; width: 15em; padding-right: 1em;}'
                    '#html-index-dir-info { margin: 1em auto 0.5em 2em; }'
                    '#html-index-footer { margin: 1em auto 0.5em 2em; font-size: smaller;}'
                    '.dir, .back, .file { background-repeat: no-repeat; background-position: 2px 4px;}'
                    '.back { background-image: url(\'${base_url}back.png\'); }'
                    '.dir { background-image: url(\'${base_url}dir.png\'); }'
                    '.file { background-image: url(\'${base_url}file.png\'); }'
                    '.image { background-image: url(\'${base_url}image.png\'); }'
                    '.video { background-image: url(\'${base_url}video.png\'); }'
                    '.music { background-image: url(\'${base_url}music.png\'); }'
                    '.archive { background-image: url(\'${base_url}archive.png\'); }'
                    '.package { background-image: url(\'${base_url}package.png\'); }'
                    '.pdf { background-image: url(\'${base_url}pdf.png\'); }'
                    '.txt { background-image: url(\'${base_url}txt.png\'); }'
                    '.markup { background-image: url(\'${base_url}markup.png\'); }'
                    '.code { background-image: url(\'${base_url}code.png\'); }'
                    '.font { background-image: url(\'${base_url}font.png\'); }'
                    '.document { background-image: url(\'${base_url}document.png\'); }'
                    '.spreadsheet { background-image: url(\'${base_url}spreadsheet.png\'); }'
                    '.presentation { background-image: url(\'${base_url}presentation.png\'); }'
                    '.application { background-image: url(\'${base_url}application.png\'); }'
                    '.plugin { background-image: url(\'${base_url}plugin.png\'); }'
                    '.iso { background-image: url(\'${base_url}iso.png\'); }'
                '</style>'
                '<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>'
                '<script>'
                    'function sort() {'
                        'column = $(this).attr("class").split(" ")[0];'
                        '$("#direction").remove();'
                        'if ($(this).hasClass("desc")) {'
                            '$("#html-index-list thead tr th").each(function(i) { $(this).removeClass("asc").removeClass("desc") });'
                            '$(this).addClass("asc");'
                            'reverse = -1;'
                        '} else {'
                            '$("#html-index-list thead tr th").each(function(i) { $(this).removeClass("asc").removeClass("desc") });'
                            '$(this).addClass("desc");'
                            'reverse = 1;'
                        '}'
                        'if (column == "name") {'
                            '$(this).append("<img src=\\"${base_url}"+((reverse == 1) ? "desc" : "asc")+".png\\" id=\\"direction\\" />");'
                        '} else {'
                            '$(this).prepend("<img src=\\"${base_url}"+((reverse == 1) ? "desc" : "asc")+".png\\" id=\\"direction\\" />");'
                        '}'
                        'rows = $("#html-index-list tbody tr").detach();'
                        'rows.sort(function(a, b) {'
                            'result = $(a).data("type") - $(b).data("type");'
                            'if (result != 0) { return result; }'
                            'return (($(a).data(column) < $(b).data(column)) - ($(a).data(column) > $(b).data(column))) * reverse;'
                        '});'
                        '$("#html-index-list tbody").append(rows);'
                    '}'
                    'function prepare() {'
                        '$("#html-index-list tbody tr").each(function(i) {'
                            'if ($(this).children(".name").hasClass("back")) {'
                               ' $(this).data("type", 1);'
                            '} else if ($(this).children(".name").hasClass("dir")) {'
                                '$(this).data("type", 2);'
                            '} else {'
                                '$(this).data("type", 3);'
                            '}'
                            '$(this).data("name", $(this).children(".name").text().toLowerCase());'
                            '$(this).data("size", parseInt($(this).children(".size").attr("sort")));'
                            '$(this).data("date", parseInt($(this).children(".date").attr("sort")));'
                        '});'
                        '$("#html-index-list thead tr th").each(function(i) {'
                            '$(this).bind("click", sort);'
                        '});'
                    '}'
                    '$(document).ready(function(){'
                        'prepare();'
                    '});'
                '</script>'
            '</head>'
            '<body>'
                '<h1 id="html-index-header">${title}</h1>'
                '<table id="html-index-list">'
                    '<thead>'
                        '<tr>'
                            '<th class="name">Name</th>'
                            '<th class="size">Size</th>'
                            '<th class="date">Last Modified</th>'
                        '</tr>'
                    '</thead>'
                    '<tbody>'
                        '${table_content}'
                    '</tbody>'
                '</table>'
                '<div id="html-index-footer">'
                    'Generated on <strong>${generation_date}</strong>'
                '</div>'
            '</body>'
        '</html>'
    )

    back_template = (
        '<tr>'
            '<td class="name back">'
                '<a href="../index.html">..</a>'
            '</td>'
            '<td class="size">'
                '&nbsp;'
            '</td>'
            '<td class="date">'
                '&nbsp;'
            '</td>'
        '</tr>'
    )

    dir_template = Template(
        '<tr>'
            '<td class="name dir">'
                '<a href="${name}/index.html">${name}</a>'
            '</td>'
            '<td class="size">'
                '&nbsp;'
            '</td>'
            '<td class="date" sort="${time_abs}">'
                '${time}'
            '</td>'
        '</tr>'
    )

    file_template = Template(
        '<tr>'
            '<td class="name file${type}">'
                '<a href="${name}">${name}</a>'
            '</td>'
            '<td class="size" sort="${size_abs}">'
                '${size}'
            '</td>'
            '<td class="date" sort="${time_abs}">'
                '${time}'
            '</td>'
        '</tr>'
    )

    def from_command_line(self):
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

        self.build_index(args.directory, args.recursive, args.searchable)

    def build_index(self, path, recursive = False, searchable = False, parent = None):
        if not os.path.isdir(path):
            print('ERROR: Directory {0} does not exist'.format(path))
            return False

        contents = [os.path.join(path, file) for file in os.listdir(path) if file != 'index.html']
        contents = [file for file in contents if not self.is_hidden(file)]

        files = [file for file in contents if os.path.isfile(file)]
        files.sort(key = str.lower)

        if recursive:
            dirs = [file for file in contents if os.path.isdir(file)]
            dirs.sort(key = str.lower)
        else:
            dirs = []

        index_file = open(os.path.join(path, 'index.html'), 'w')
        index_file.write(self.build_html(path, parent, dirs, files, searchable))
        index_file.close()

        print('Created index.html for ' + os.path.realpath(path))

        for dir in dirs:
            self.build_index(dir, recursive, searchable, path)

        return True

    def is_hidden(self, filepath):
        filename = os.path.basename(os.path.abspath(filepath))
        return filename.startswith('.') or self.has_hidden_attribute(filepath)

    def has_hidden_attribute(self, filepath):
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
            if attrs == -1:
                return False

            return bool(attrs & 2)

        except (AttributeError):
            return False

    def build_html(self, path, parent, dirs, files, searchable):
        table_content = ''

        if parent:
            table_content += self.back_template

        for dir in dirs:
            table_content += self.dir_template.safe_substitute({
                'name': os.path.basename(dir),
                'time': self.format_date(time.localtime(os.path.getmtime(dir))),
                'time_abs': os.path.getmtime(dir),
            })

        for file in files:
            table_content += self.file_template.safe_substitute({
                'name': os.path.basename(file),
                'type': self.get_filetype(os.path.basename(file)),
                'size': self.get_readable_size(file),
                'size_abs': os.path.getsize(file),
                'time': self.format_date(time.localtime(os.path.getmtime(file))),
                'time_abs': os.path.getmtime(file),
            })

        return self.page_template.safe_substitute({
            'base_url': self.image_base_url,
            'robots': not searchable and 'noindex, nofollow' or '',
            'title': os.path.basename(os.path.realpath(path)),
            'table_content': table_content,
            'generation_date': self.format_date(time.localtime()),
        })

    def get_filetype(self, file_name):
        ext = file_name.rsplit('.', 1)[-1].lower()
        for keys, value in self.file_types.items():
            if ext in keys:
                return ' ' + value

        return ''

    def get_readable_size(self, file):
        size = os.path.getsize(file)

        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
            if abs(size) < 1024.0:
                return '{:3.1f} {}'.format(size, unit)

            size /= 1024.0

        return '{:3.1f} YB'.format(size)

if __name__ == '__main__':
    HtmlIndex().from_command_line()
