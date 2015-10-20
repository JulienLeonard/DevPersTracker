MAIN_TEMPLATE = """\
<head>
  <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
</head>
    <div align="center">
    <h1>Goals</h1>
    <table>
    <tr>
    <td>
    <form action="/listgoals" method="get">
      <div><input type="submit" value="List"></div>
    </form>
    </td>
    <td>
    <form action="/addgoal" method="get">
      <div><input type="submit" value="Add"></div>
    </form>
    </td>
    </tr>
    </table
    </hr>
    </div>
"""
