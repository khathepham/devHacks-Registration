import env from './env.json' with {type: 'json'}
import c from '@notionhq/client'
import fetch from 'node-fetch'

const notion = new c.Client({ auth: env.notion_pass });


const Status = {
    InProgress: Symbol("In Progress"),
    Sent: Symbol("Sent"),
    Failed: Symbol("Failed to Send")
}

async function getRowsToResend() {
    const dbID = env.notion_database
    const response = await notion.databases.query({
        database_id: dbID,
        filter: {
            property: 'Resend Ticket',
            checkbox: {
                equals: true
            }
        }
    })
    return response.results
}

async function updateStatus(status, pageID){
    let response = await notion.pages.update({
        page_id: pageID,
        properties: {
            "Resend Ticket Status": {
                select: {name: status}
            }
        }
    })

    if('status' in response && (response.status === 406 || response.status === 429)){
        sleep(3000).then(() => {
            response = updateStatus(status, pageID)
        })
    }
    return response;
}

async function updateCheckbox(isChecked, pageID){
    let response =  await notion.pages.update({
        page_id: pageID,
        properties: {
            "Resend Ticket": {
                checkbox: isChecked
            }
        }
    })

    if('status' in response && (response.status === 406 || response.status === 429)){
        sleep(3000).then(() => {
            response = updateCheckbox(isChecked, pageID)
        })
    }
}

async function sendEmail(pageID){
    const url = "https://devhacks2024.khathepham.com/register-devhacks-2024/resend_email/" + pageID;
    let is200 = false;
    let r = null;
    console.log("Sending POST Reqeust to Email Server.")
    await fetch(url, {
        method: "POST",
        body: null
    })
    .then(
        response => {
            is200 = response.status === 200;
            console.log(`${response.status} - ${response.statusText}`)

        },
    );

    return is200
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


getRowsToResend().then(
    function (value){
        for (const ticket of value) {
            console.log(`Page ID: ${ticket.id}`)
            updateStatus(Status.InProgress.description, ticket.id).then()
            sendEmail(ticket.id).then(x => {
                if(x){
                    updateStatus(Status.Sent.description, ticket.id).then();
                    updateCheckbox(false, ticket.id).then();
                }
                else {
                    updateStatus(Status.Failed.description, ticket.id).then();
                }
            })
        }
    }
)