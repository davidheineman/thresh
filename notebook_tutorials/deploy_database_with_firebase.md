## Deploy a Database for Annotations

Thresh was intentionally built with a bring-your-own-database approach to allow users to plug in the Thresh interface into any existing annotation application. However, when building your own annotation setup, you may need to host an endpoint to collect and host annotated entries. In this tutorial, we will walk through using a [**Firebase database**](https://firebase.google.com/) with Thresh! You may use this independent or alongside a crowdsource deployment.

### Getting Started

Using “Firestore Database” on Firebase (see pricing here: [**firebase.google.com/pricing**](https://firebase.google.com/pricing)). Note Google Cloud is the only provider with a *permanent free option*, so as long as you stay under the limits (fairly generous for this use case), you will not be charged.

Create a new *collection* named `thresh` and a *document* named `annotations` in the Cloud Firestore.

I use this (very permissive) security rule. It allows *anyone to write anything to the datastore*. However, it does not allow anyone to read.

```javascript
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow write
    }
  }
}
```

Then add this to the annotation config file to have it point to Firebase when users click the "Submit" button (see: [**thresh.tools/?t=demo_crowdsource**](thresh.tools/?t=demo_crowdsource)):

```yaml
crowdsource: "custom"       # Use "prolific" or other crowdsource options here, "custom" for your own database setup
database: 
    type: firebase
    project_id: [your-project-id]
    url: https://[your-project-id].firebaseio.com/
    # collection: thresh     # (default: thresh) The database to use, this must exist on the firestore
    # document: annotation   # (default: annotation) The document to use, this must exist on the firestore
    field: annotation_set_1  # The document field to store annotations, we recommend changing this value between data collection runs
```

Now you may click through your template with this extra configuration and press “Submit”, you should see this in Firebase:

<div align="center">
    <img src="../public/img/firebase.png" width="600" />
</div>

The annotations will be uploaded to Firebase *just as if they were downloaded from the interface*. Make sure to be careful when assembling your data to encode the annotator information, etc. so it is passed through correctly.