<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'/usr/lib/python2.4/site-packages/raa/templates/master.kid'">
<!--
    Copyright (c) 2005-2006 rPath, Inc.
    All Rights Reserved
-->
<head>
  <title>Delete User</title>
  <style type="text/css">
    p#warn {
      text-decoration: italic;
      color: #ff0000;
    }
    button#cancelb {
      position: relative;
      top: -50px
      left: -40%;
    }
    button#okb {
      position: relative;
      top: -50px
      left: -40%;
    }
  </style>
</head>
<body>
  <div class="tabs">
    <ul>
      <li><a href="index"><span>Users</span></a></li>
      <li><a href="add"><span>Add User</span></a></li> 
      <li class="current"><a href="#"><span>Delete User</span></a></li> 
     </ul>
  </div>
  <br/>
  <p>
   <hr />
  </p>
    <div id="del">
      <h3>Confirm:</h3>
      <p id="warn">Delete the conary user "${username}"?</p>
       <form action="deleteUser" method="POST">
         <input type="hidden" name="username" value="${username}"/>
         <input type="hidden" name="confirm" value="True"/>
         <button class="img" type="submit"><img src="${tg.url('/static/images/ok_button.png')}" alt="Delete User" />
         </button>
       </form>
       <a href="index"><button type="button" class="img"><img src="${tg.url('/static/images/cancel_button.png')}" alt="Cancel" /></button></a>
    </div>
</body>
</html>
<!-- vim: set ts=2 sw=2 sts=2 expandtab autoindent: -->
