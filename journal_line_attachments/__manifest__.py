{
    "name": "Journal Line Attachments",
    "version": "1.0",
    "summary": "Attach multiple documents to journal lines and view them from journal entry",
    "category": "Accounting",
    "depends": ["account","base"],
    "data": [
        "views/account_move_line_views.xml",
        "views/account_move_views.xml",
        # "views/ir_attachment_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
