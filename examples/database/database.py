"""
Copyright (C) 2014, Zoomer Analytics LLC.
All rights reserved.

Version: 0.1.0
License: BSD 3-clause (see LICENSE.txt for details)
"""
import sqlite3
import os
from xlwings import Workbook, Range

# Make a connection to the calling Excel file
wb = Workbook()

# Place the database next to the Excel file
db_file = os.path.join(os.path.dirname(wb.fullname), 'chinook.sqlite')

# Database connection and creation of cursor
con = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
cursor = con.cursor()


def playlist():
    """
    Get the playlist content based on the ID from the Dropdown
    """

    # Get PlaylistId from ComboBox
    playlist_id = wb.com_workbook.ActiveSheet.OLEObjects("ComboBox1").Object.Value

    # Database query
    cursor.execute(
        """
        SELECT
        t.Name AS Track, alb.Title AS Album,  art.Name AS Artist, t.Composer
        FROM PlaylistTrack pt
        INNER JOIN Track t ON pt.TrackId = t.TrackId
        INNER JOIN Album alb ON t.AlbumId = alb.AlbumId
        INNER JOIN Artist art ON alb.ArtistId = art.ArtistId
        WHERE PlaylistId = ?
        """, (playlist_id,))

    # Get the result and column names
    col_names = [col[0] for col in cursor.description]
    rows = cursor.fetchall()

    # Clear the sheet and write the column names and result to Excel
    Range('A9').table.clear_contents()
    Range('A9').value = col_names
    if len(rows):
        Range('A10').value = rows
    else:
        Range('A10').value = 'Empty Playlist!'

    # Close cursor and connection
    cursor.close()
    con.close()


def combobox():
    """
    This populates the ComboBox with the values from the database
    """

    # Database Query
    cursor.execute("SELECT PlaylistId, Name FROM Playlist")

    # Write IDs and Names to hidden sheet
    Range('Source', 'A1').table.clear_contents()
    Range('Source', 'A1').value = cursor.fetchall()

    # Format and fill the ComboBox to show Names (Text) and give back IDs (Values)
    # TODO: implement natively in xlwings
    combo = "ComboBox1"
    wb.com_workbook.ActiveSheet.OLEObjects(combo).Object.ListFillRange = \
        'Source!{}'.format(str(Range('Source', 'A1').table.com_range.Address))
    wb.com_workbook.ActiveSheet.OLEObjects(combo).Object.BoundColumn = 1
    wb.com_workbook.ActiveSheet.OLEObjects(combo).Object.ColumnCount = 2
    wb.com_workbook.ActiveSheet.OLEObjects(combo).Object.ColumnWidths = 0

    # Close cursor and connection
    cursor.close()
    con.close()
