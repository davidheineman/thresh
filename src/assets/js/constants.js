export const DOWNLOAD_INTERFACE_HTML_NAME = "interface.html";
export const DOWNLOAD_INTERFACE_NAME = "interface.yml";
export const DOWNLOAD_FILE_NAME = "annotations.json";

export const COLORS = {
    'red': '#ee2a2a',
    'green': '#64c466',
    'blue': '#2186eb',
    'yellow': '#f7ce46',
    'teal': '#3ca3a7',
    'orange': '#e67c43'
}

export const LIKERT_COLOR_MAP = {
    'minor': 'light-blue',
    'somewhat': 'light-orange',
    'a lot': 'light-red',
}

export const INTERFACE_HTML_TEMPLATE = `
<!DOCTYPE html>
<html>
  <head>
    <title>{template_name}</title>
    <script src="https://code.jquery.com/jquery-3.5.1.js" crossorigin="anonymous"></script>
  </head>
  <body></body>
  <script>
var template = \`
{template}
\`;
var data = \`
{data}
\`;

    // Heads up! The best practice is to host your interface.yml and data.json files on GitHub and use the following URL format:
    // var ghParameter = "davidheineman/salsa/main/interface.yml";      // <- Add GitHub path to host interface.yml instead!
    // var dParameter = "demo_data.json";                               // <- Add data to show up on load!
    // iframeUrl = "https://thresh.tools/?gh=" + encodeURIComponent(ghParameter) + "&d=" + encodeURIComponent(dParameter);

    iframeUrl = "https://thresh.tools/custom"

    var iframe = document.createElement('iframe');
    iframe.src = iframeUrl;
    Object.assign(iframe.style, {
        position: 'fixed', top: '0', left: '0', width: '100%', height: '100%', border: 'none'
    });
    document.body.appendChild(iframe);

    // Sends our interface & data to the iframe
    $('#iframe').on("load", function() {
        $('#iframe')[0].contentWindow.postMessage({
          template: template,
          data: data
        }, 'https://thresh.tools');
      })
  </script>
</html>
`;