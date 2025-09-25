from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Handler pour les erreurs de validation (422)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0] if errors else None

    if first_error and "email" in first_error["loc"]:
        message = "L'adresse email n'est pas valide."
    elif first_error and "password" in first_error["loc"]:
        message = "Le mot de passe est invalide."
    else:
        message = first_error["msg"] if first_error else "Erreur de validation."

    return JSONResponse(
        status_code=422,
        content={"detail": message}
    )
