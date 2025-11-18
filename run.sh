#!/bin/bash
set -e

EXPORTS="$(dirname "$0")/exports"
DEST="$(dirname "$0")/container_root/home/user"

echo "Preparing workspace..."
mkdir -p "$DEST"

# Load saves ascending (oldest -> newest)
mapfile -t SAVES < <(ls -1 "$EXPORTS" | sort 2>/dev/null || true)
TOTAL=${#SAVES[@]}
PER_PAGE=9
PAGE=1

show_menu() {
    clear
    echo "==============================="
    echo "         AVAILABLE SAVES"
    echo "==============================="
    echo

    START=$(( (PAGE-1)*PER_PAGE ))
    END=$(( START+PER_PAGE-1 ))
    if [ $END -ge $TOTAL ]; then END=$((TOTAL-1)); fi

    echo "Page $PAGE ($((START+1)) - $((END+1)) of $TOTAL)"
    echo

    SLOT=1
    for ((i=START; i<=END; i++)); do
        echo " $SLOT. ${SAVES[$i]}"
        ((SLOT++))
    done

    echo " 0. Run empty workspace"

    if [ $TOTAL -gt $PER_PAGE ]; then
        echo
        echo "Commands: n=next page, p=previous page, number=select"
    fi

    echo
}

while true; do
    show_menu
    read -p "Select option: " CHOICE

    if [[ "$CHOICE" == "0" ]]; then break; fi

    if [[ "$CHOICE" == "n" ]]; then
        MAXPAGE=$(( (TOTAL+PER_PAGE-1)/PER_PAGE ))
        if [ $PAGE -lt $MAXPAGE ]; then ((PAGE++)); fi
        continue
    fi

    if [[ "$CHOICE" == "p" ]]; then
        if [ $PAGE -gt 1 ]; then ((PAGE--)); fi
        continue
    fi

    if [[ "$CHOICE" =~ ^[1-9]$ ]]; then
        GLOBAL_INDEX=$(( (PAGE-1)*PER_PAGE + CHOICE -1 ))
        if [ $GLOBAL_INDEX -lt $TOTAL ]; then
            SELECTED="${SAVES[$GLOBAL_INDEX]}"
            echo "Selected: $SELECTED"
            cp "$EXPORTS/$SELECTED" "$DEST/"

            cd "$DEST"
            case "$SELECTED" in
                *.zip) unzip -o "$SELECTED" ;;
                *.tar|*.tar.gz|*.tgz) tar -xf "$SELECTED" ;;
            esac
            rm "$SELECTED"
            cd - > /dev/null
            break
        fi
    fi
done

echo "Building Docker image..."
docker build -t console-file-manager:latest .

clear
echo "Running container..."
docker-compose run --rm fm

echo "Cleaning workspace..."
find "$DEST" -mindepth 1 -delete

clear
