<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">
<!--
    Copyright (c) 2005-2006 rPath, Inc.
    All Rights Reserved
-->
<head>
  <title>Update Mirroring Privileges</title>
</head>
<body>
  <div class="tabs">
    <ul>
      <li class="current"><a href="index"><span>Users</span></a></li>
      <li><a href="add"><span>Add User</span></a></li> 
     </ul>
  </div>
  <br/>
  <p>
   <hr />
  </p>
    <div id="users" py:if="userData">
    <h5>The following users have permission to access this repository.  Users with the "Mirroring" permission are allowed to mirrror to this repository.</h5>
    <table class="list" cellspacing="0">
    <thead>
      <tr>
         <th align="left">User</th>
         <th align="left" id="logItemHeading">Permission</th>
         <th align="left" id="logItemHeading">Options</th>
      </tr>
    </thead>
    <tbody style="height : auto; overflow: auto; padding-right: 2em; ">
      <tr py:for="x in userData" py:attrs="{'class': x[2]}" >
         <td valign="top" align="center" id="logItem" width="130">${x[0]}</td>
         <td valign="top" align="center" id="logItem">${x[1]}</td>
         <td valign="top" align="center" id="logItem"><a href="deleteUser?username=${x[0]}">Delete</a> | <a href="changePassword?username=${x[0]}">Password</a></td>
      </tr>
    </tbody>
    </table>
    </div>
    <div py:if="not userData"><h5>There are currently no conary users on this system.  Click the "Add User" tab to create one.  To mirror to this repository, a user must have Mirroring permission.</h5></div> 
</body>
</html>
<!-- vim: set ts=2 sw=2 sts=2 expandtab autoindent: -->
