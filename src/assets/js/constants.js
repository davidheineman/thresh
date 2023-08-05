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

    const targetOrigin = 'https://thresh.tools';
    const retryInterval = 2000;

    // Sends our interface & data to the iframe
    function postMessageWithRetry(template, data) {
      const maxRetryAttempts = 2; 
      let retryCount = 0;

      function tryPostMessage() {
        try {
          const response = $('#iframe')[0].contentWindow.postMessage({ template: template, data: data }, targetOrigin);
        } catch (error) {
          console.error('Error sending postMessage:', error);
        }

        if (retryCount < maxRetryAttempts) {
          retryCount++;
          console.warn('Retrying in ' + retryInterval + ' milliseconds (attempt ' + retryCount + '}).');
          setTimeout(tryPostMessage, retryInterval);
        }
      }

      tryPostMessage();
    }

    // Create the iframe
    var iframe = $('<iframe>', {
      src: targetOrigin + '/custom',
      id: 'iframe',
    }).on("load", function() {
      setTimeout(postMessageWithRetry(template, data), retryInterval);
    }).css({ position: 'fixed', top: '0', left: '0', width: '100%', height: '100%', border: 'none' });

    $('body').append(iframe);
  </script>
</html>
`;