const vscode = require('vscode');
const path = require('path');

/**
 * @param {vscode.ExtensionContext} context
 */


/**
 * @param {vscode.TextDocument} document
 * @param {vscode.DiagnosticCollection} collection
 */
function updateDiagnostics(document, collection, msg, duplicate_line_nos) {
	collection.clear();
	if (duplicate_line_nos == null){
		return;
	}

	var message_list = []
	for(var j = 0; j < duplicate_line_nos.length; j++){
		var line_nos = duplicate_line_nos[j];
		var relatedInformationList = []
		for (var i = 0; i < line_nos.length; i++) {
			relatedInformationList.push(new vscode.DiagnosticRelatedInformation(new vscode.Location(document.uri, new vscode.Range(new vscode.Position(line_nos[i], 0), new vscode.Position(line_nos[i], 0))), 'url resemblance found'));
		}

		for (var i = 0; i < line_nos.length; i++) {
			message_list.push({
				code: '',
				message: msg,
				range: new vscode.Range(new vscode.Position(line_nos[i], 0), new vscode.Position(line_nos[i], 0)),
				severity: vscode.DiagnosticSeverity.Error,
				source: '',
				relatedInformation: relatedInformationList
			});
		}
	}

	if (document && message_list.length > 0) {
		collection.set(document.uri, message_list);	
	}
}

function regexMatchAll(regex, str) { 
	const array = [...str.matchAll(regex)]; 
	var result = []
    for(var i = 0; i < array.length; i++) {
		result.push(array[i][1]);
    }
	return result;
} 

function run_validate(context) {
	const execSync = require("child_process").execSync; 
	var output = execSync('python3 ' + '"' + context.extensionUri.path + '/python-scripts/url_resemblance.py' + '" ' + '"'  +  vscode.window.activeTextEditor.document.uri.path + '"').toString().trim() ;
	if (output == "exited"){
		return []
	}else{
		const regex = /route matched in line number ([0-9\,]*) found/g; 
		var matches = regexMatchAll(regex, output)
		var duplicate_line_nos = []
		for(var i = 0; i < matches.length; i++){
			duplicate_line_nos.push(JSON.parse("[" + matches[i] + "]"));
		}
		return duplicate_line_nos
	}
}

function activate(context) {
	let disposable = vscode.commands.registerCommand('url-resemblance.url_resemblance', async function () {
		vscode.window.showInformationMessage('Hello from Ambitious Coder');
		const collection = vscode.languages.createDiagnosticCollection('test');
		if (vscode.window.activeTextEditor && vscode.window.activeTextEditor.document && path.basename(vscode.window.activeTextEditor.document.uri.fsPath) === 'routes.go') {
			var line_nos = run_validate(context);
			updateDiagnostics(vscode.window.activeTextEditor.document, collection, "URL matching multiple routes", line_nos);
		}

		context.subscriptions.push(
			vscode.workspace.onDidSaveTextDocument(
				document => {
					if (document) {
						if (path.basename(document.uri.fsPath) === 'routes.go') {
							var line_nos = run_validate(context);
							updateDiagnostics(document, collection, "URL matching multiple routes", line_nos);
						}
					}
				}
			)
		)		
	});

	context.subscriptions.push(disposable);
	vscode.commands.executeCommand("url-resemblance.url_resemblance");
}

// This method is called when your extension is deactivated
function deactivate() {
	console.log('Deactivitig sucussfully');
}

module.exports = {
	activate,
	deactivate
}
