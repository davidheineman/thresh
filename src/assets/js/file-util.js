import { DOWNLOAD_FILE_NAME } from './constants.js';

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