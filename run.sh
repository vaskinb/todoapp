#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# --- Start script ---
# -----------------------------------------------------------------------------
if [ "$1" = "" ]; then
    echo "Main usage:
    ./run.sh setup -- to run setup project process
    ./run.sh admin -- to run web Admin server
    ./run.sh db [migrate, upgrade] -- to run migration script
    "
else
    case "$1" in
        freeze)
            # -----------------------------------------------------------------
            # --- Save requirements to file ---
            # -----------------------------------------------------------------
            pip freeze | grep -v "pkg-resources" > requirements.txt
        ;;
        db)
            # -----------------------------------------------------------------
            # --- Migrations ---
            # -----------------------------------------------------------------
            export FLASK_APP='manage'
            flask db $2
        ;;
        tests)
            # -----------------------------------------------------------------
            # --- Run pytests ---
            # -----------------------------------------------------------------
            export FLASK_CONFIG="test"
            echo "MODE: ${FLASK_CONFIG}"
            source ./env.pytests
            pytest -s "$2" -W ignore::DeprecationWarning
        ;;
        coverage)
            # -----------------------------------------------------------------
            # --- Run coverage ---
            # -----------------------------------------------------------------
            export FLASK_CONFIG="test"
            echo "MODE: ${FLASK_CONFIG}"
            pytest \
                --cov=app \
                --cov-report=term-missing \
                -s tests/ -W ignore::DeprecationWarning
        ;;
        *)
            # -----------------------------------------------------------------
            # --- Run scripts ---
            # -----------------------------------------------------------------
            python ./manage.py "$@"
    esac
fi
