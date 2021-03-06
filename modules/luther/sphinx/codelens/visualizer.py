# Copyright (C) 2011  Bradley N. Miller
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'bmiller'

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from pg_logger import exec_script_str_local
import json

def setup(app):
    app.add_directive('codelens',Codelens)
    app.add_stylesheet('pytutor.css')
    app.add_stylesheet('jquery-ui-1.8.24.custom.css')

    app.add_javascript('d3.v2.min.js')
    app.add_javascript('jquery.ba-bbq.min.js')
    app.add_javascript('jquery.jsPlumb-1.3.10-all-min.js')
    app.add_javascript('jquery-ui-1.8.24.custom.min.js')
    app.add_javascript('jquery.textarea.js')
    app.add_javascript('pytutor.js')



VIS = '''
<div id="%(divid)s"></div>
<p class="cl_caption"><span class="cl_caption_text">%(caption)s (%(divid)s)</span> </p>'''

DATA = '''
<script type="text/javascript">
%(tracedata)s

$(document).ready(function() {
    %(divid)s_vis = new ExecutionVisualizer('%(divid)s',%(divid)s_trace,
                                {embeddedMode: %(embedded)s,
                                verticalStack: true,
                                redrawAllConnectorsOnHeightChange: true,
                                codeDivWidth: 500
                                });
    attachLoggers(%(divid)s_vis,'%(divid)s');
});

$(window).resize(function() {
    %(divid)s_vis.redrawConnectors();
});
</script>
'''


class Codelens(Directive):
    required_arguments = 1
    optional_arguments = 1
    option_spec = {
        'tracedata':directives.unchanged,
        'caption':directives.unchanged,
        'showoutput':directives.flag
    }

    has_content = True

    def run(self):

        self.JS_VARNAME = ""
        self.JS_VARVAL = ""

        def js_var_finalizer(input_code, output_trace):
          global JS_VARNAME
          ret = dict(code=input_code, trace=output_trace)
          json_output = json.dumps(ret, indent=None)
          return "var %s = %s;" % (self.JS_VARNAME, json_output)


        self.options['divid'] = self.arguments[0]
        if self.content:
            source = "\n".join(self.content)
        else:
            source = '\n'

        CUMULATIVE_MODE=False
        self.JS_VARNAME = self.options['divid']+'_trace'
        if 'showoutput' not in self.options:
            self.options['embedded'] = 'true'  # to set embeddedmode to true
        else:
            self.options['embedded'] = 'false'

        self.options['tracedata'] = exec_script_str_local(source, CUMULATIVE_MODE, js_var_finalizer)
        res = VIS
        if 'caption' not in self.options:
            self.options['caption'] = ''
        if 'tracedata' in self.options:
            res += DATA
        return [nodes.raw('',res % self.options,format='html')]

