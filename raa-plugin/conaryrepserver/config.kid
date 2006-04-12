<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../../templates/master.kid'">

<head>
    <title>Set the Conary Server Hostname</title>
</head>

<body>
    <div id="ServerName">
        <h2>Update Conary Server Hostname</h2>
        <span py:if="not editable">
            <font color="#FF0000">
            <p>${pageText}</p>
            </font>
        </span>
        <span py:if="editable">
            <p>${pageText}</p>
        </span>
        <hr />
        <p><h3>Current Conary Server Hostname:</h3>
            <i>${data}</i>
        </p>
        <span py:if="editable">
            <form action="chsrvname" method="POST">
                <div class="label">
                    <label for="servername"><h3>New Conary Server Hostname:</h3></label>
                </div>
                <div class="field">
                    <input type="text" id="servername" name="newsrv" size="50"/>
                </div>
                <center>
                <button type="submit" class="img"><img alt="apply" src="/static/images/apply_button.png"/></button>
                </center>
            </form>
        </span>
    </div>
</body>
</html>
