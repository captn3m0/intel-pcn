import asyncio
import csv
from pyppeteer import launch

async def main(csv_writer, year):
    browser = await launch(executablePath='/usr/sbin/chromium', headless=True)
    page = await browser.newPage()
    page.setDefaultNavigationTimeout(0)
    await page.goto("https://qdms.intel.com/Portal/SearchPCNDataBase.aspx")

    # Fill in start and end dates
    start = await page.querySelector("#ctl00_PCMSMainContent_dtpStartDate")
    print(f'(el)=> el.value = "01/01/{year}"')
    await page.evaluate(f'(el)=> el.value = "01/01/{year}"', start)
    end = await page.querySelector("#ctl00_PCMSMainContent_dtpEndDate")
    await page.evaluate(f'(el)=> el.value = "01/01/{year+1}"', end)

    await page.select('#ctl00_PCMSMainContent_ddlResultSize', '50')
    # wait for 30000
    # await page.waitFor(30000)


    # Click the search button
    btn = await page.querySelector("#ctl00_PCMSMainContent_btnSearch")
    await btn.click()

    data = []
    starting_index = 1

    while True:
        # Wait for rows to load
        await page.waitForSelector(".GridViewRow, .GridViewAltRow")
        rows = await page.querySelectorAll(".GridViewRow, .GridViewAltRow")

        for row in rows:
            columns = await row.querySelectorAll("td")

            row_data = [
                await page.evaluate("(element) => element.textContent", column) for column in columns[1:]
            ] + [
                await page.evaluate("(element) => element.children[0].getAttribute('href')", columns[1])
            ]
            csv_writer.writerow(row_data)
        
        
        await page.querySelectorAllEval(".GridViewRow, .GridViewAltRow", '(nodes)=>nodes.map(el=>el.remove())')
        assert(len(await page.querySelectorAll(".GridViewRow, .GridViewAltRow")) == 0)
        
        paginator = (await page.querySelectorAll('tr.GridViewPager'))[0]
        elements = await paginator.querySelectorAll("td>table>tbody>tr>td")
        
        currentPage = False
        nextBtn = None
        starting_index += 1
        print(f"Planning to click {starting_index}")
        
        # iterate with an index over elements
        for element in elements:
            text = await page.evaluate("(x)=> x.textContent", element)
            if (text).strip() == str(starting_index):
                nextBtn = element
                break

        if not nextBtn:
            print("No more pages")
            break
        else:
            await nextBtn.click()
            await page.waitFor(2000)        

    await browser.close()

with open("pcn_data.csv", "a", newline="", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)
    # csv_writer.writerow(["PCN Number", "Publish Date", "PCN Title", "Key Characteristics", "Product Categories", "Abstract", "URL"])
    for year in range(2022, 2024):
        asyncio.get_event_loop().run_until_complete(main(csv_writer, year))
