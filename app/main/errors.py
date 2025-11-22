from . import main

@main.app_errorhandler(400)
def error_400(error):
    return {"success": False, "error": 400, "message": error.description}, 400


@main.app_errorhandler(404)
def error_404(error):
    return {"success": False, "error": 404, "message": error.description}, 404


@main.app_errorhandler(500)
def error_500(error):
    return {"success": False, "error": 500, "message": error.description}, 500
