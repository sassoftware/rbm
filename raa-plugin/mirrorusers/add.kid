<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../../templates/master.kid'">
<head>
  <title>Update Mirroring Privileges"</title>
  <style type="text/css">
    p#errMessage {
      text-decoration: italic;
      color: #ff0000;
    }
    p#normMessage {
      text-decoration: italic;
    }
  </style>
</head>
<body>
  <div class="tabs">
    <ul>
      <li><a href="index"><span>Users</span></a></li>
      <li class="current"><a href="add"><span>Add User</span></a></li> 
     </ul>
  </div>
  <br/>
  <p>
   <hr />
  </p>
    <div id="add">
      <p py:if="error" id="errMessage"><i>${message}</i></p>
      <p py:if="not error" id="normMessage"><i>${message}</i></p>
       <form action="add" method="POST">
           <table>
                <tr>
                    <td class="label">
                        <label>User Name</label>
                    </td>
                    <td class="field">
                        <input type="text" name="username" size="40"/>
                    </td>
                </tr>
                <tr>
                    <td class="label">
                        <label>Password</label>
                    </td>
                    <td class="field">
                        <input type="password" name="passwd1" size="40" />
                    </td>
                </tr>
                <tr>
                    <td class="label">
                        <label>Password Again</label>
                    </td>
                    <td class="field">
                        <input type="password" name="passwd2" size="40" />
                    </td>
                </tr>
                <tr>
                    <td colspan="2" class="buttons">
                        <button class="img" type="submit">
                          <img src="${tg.url('/static/images/apply_button.png')}" alt="Change Password" />
                        </button>
                    </td>
                </tr>
            </table>
       </form>
    </div>
</body>
</html>
<!-- vim: set ts=2 sw=2 sts=2 expandtab autoindent: -->
