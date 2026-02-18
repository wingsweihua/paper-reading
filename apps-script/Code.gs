/**
 * 部署为「网络应用」后，用 GET 请求带参数调用即可向当前表格插入一行。
 * 插入到表头下面第一行，时间最近的 paper 在最上面。
 * 参数: title, authors, paper_link （均为可选，会做基本编码处理）
 * 表格列顺序: Date and time | Title | Authors and Affiliation | Takeaway | Paper link
 */
function doGet(e) {
  var params = e.parameter;
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var now = new Date();
  var dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  var title = (params.title != null) ? decodeURIComponent(params.title) : '';
  var authors = (params.authors != null) ? decodeURIComponent(params.authors) : '';
  var paperLink = (params.paper_link != null) ? decodeURIComponent(params.paper_link) : '';
  sheet.insertRowBefore(2);
  sheet.getRange(2, 1, 2, 5).setValues([[dateStr, title, authors, '', paperLink]]);
  return ContentService.createTextOutput(JSON.stringify({ ok: true, message: 'Added to sheet' }))
    .setMimeType(ContentService.MimeType.JSON);
}
