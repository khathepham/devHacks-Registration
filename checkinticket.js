const { Client } = require('@notionhq/client');

if(!process.argv[2] || !process.argv[3])
    console.log("Not the Correct Arguments")

const notion = new Client({ auth: process.argv[2] });

(async () => {
    const pageId = process.argv[3];
    const response = await notion.pages.update({
        page_id: pageId,
        properties: {
            'Checked In': {
                checkbox: true,
          },
        },
    });
    console.log(JSON.stringify(response));
})();