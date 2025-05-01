function doGet(e) {
  var cal = CalendarApp.getOwnedCalendarById("your gmail");

  if (cal == undefined) {
    return ContentService.createTextOutput(
      JSON.stringify({ error: "Calendar not found" })
    ).setMimeType(ContentService.MimeType.JSON);
  }

  // Set time range: now to 24 hours later
  var now = new Date();
  var next24h = new Date(now.getTime() + 24 * 60 * 60 * 1000); // Add 24 hours

  var events = cal.getEvents(now, next24h);
  var result = [];

  for (var i = 0; i < events.length; i++) {
    result.push({
      summary: events[i].getTitle(),
      start: events[i].getStartTime().toISOString(),
      end: events[i].getEndTime().toISOString()
    });
  }

  return ContentService.createTextOutput(JSON.stringify(result))
                       .setMimeType(ContentService.MimeType.JSON);
}
