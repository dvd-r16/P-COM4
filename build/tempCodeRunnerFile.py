def on_closing():
    if after_id_principal:
        window.after_cancel(after_id_principal)
    if after_id_diag:
        window.after_cancel(after_id_diag)
        
    window.destroy()
    sys.exit()

window.protocol("WM_DELETE_WINDOW", on_closing)