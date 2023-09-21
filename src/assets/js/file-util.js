import { DOWNLOAD_FILE_NAME, DOWNLOAD_INTERFACE_NAME, DOWNLOAD_INTERFACE_HTML_NAME, INTERFACE_HTML_TEMPLATE } from './constants.js';

export async function parseJsonFile(file) {
    return new Promise((resolve, reject) => {
        const fileReader = new FileReader()
        fileReader.onload = e => resolve(JSON.parse(e.target.result))
        fileReader.onerror = error => reject(error)
        fileReader.readAsText(file)
    })
}

export async function handle_file_upload(e) {
    let file = e.target.files[0];
    let new_data = await parseJsonFile(file);
    return new_data
}

export function handle_file_download(data, filename=DOWNLOAD_FILE_NAME) {
    var json = JSON.stringify(data);
    var url = URL.createObjectURL(new Blob([json], { type: "application/json" }));
    $("<a>").attr({ href: url, download: filename }).appendTo("body")[0].click();
    URL.revokeObjectURL(url);
}

export function handle_interface_download(template, template_name, data, html) {
    let filename;
    if (html) {
        filename = DOWNLOAD_INTERFACE_HTML_NAME;
        let out = INTERFACE_HTML_TEMPLATE;
        let data_raw = JSON.stringify(data);
        out = out.replace("{template_name}", template_name).replace("{template}", template).replace("{data}", data_raw);
        var url = URL.createObjectURL(new Blob([out], { type: "application/html" }));
    } else {
        filename = DOWNLOAD_INTERFACE_NAME;
        var url = URL.createObjectURL(new Blob([template], { type: "application/yml" }));
    }
    
    $("<a>").attr({ href: url, download: filename }).appendTo("body")[0].click();
    URL.revokeObjectURL(url);
}

export function get_file_path() {
    let urlParams = new URLSearchParams(window.location.search);
    let data_path = urlParams.get('data');
    if (data_path != null) {
        return data_path
    }
    return null
}

export function download_data(file_path) {
    return fetch(file_path)
        .then(r => r.json())
        .then(json => { return json; });
}

export function download_config(file_path) {
    return fetch(file_path)
        .then(response => response.text())
        .then(r => {return r});
}

export function joinPaths(path1, path2) {
    return path1.replace(/\/$/, '') + '/' + path2.replace(/^\//, '');
}
