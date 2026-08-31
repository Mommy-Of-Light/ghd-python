#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

EXPORTS="$SCRIPT_DIR/exports"
DEST="$SCRIPT_DIR/container_root/home/user"

IMAGE="console-file-manager:latest"

# ============================================================
# Colors
# ============================================================

RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
CYAN='\033[36m'
MAGENTA='\033[35m'
WHITE='\033[37m'
RESET='\033[0m'

# ============================================================
# Helpers
# ============================================================

pause() {
    read -rp "Press Enter to continue..."
}

clear_screen() {
    clear
}

display_delay() {
    local text="$1"
    local delay="${2:-0.25}"

    for suffix in "" "." ".." "..."; do
        clear_screen
        echo
        echo "  ${text}${suffix}"
        sleep "$delay"
    done
}

# ============================================================
# Prepare workspace
# ============================================================

echo
echo -e "${CYAN}Preparing workspace...${RESET}"

mkdir -p "$DEST"
mkdir -p "$EXPORTS"

# ============================================================
# Docker detection
# ============================================================

if ! command -v docker >/dev/null 2>&1; then
    echo
    echo -e "${RED}ERROR: Docker is not installed or not in PATH.${RESET}"
    pause
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo
    echo -e "${RED}ERROR: Docker Compose is not installed.${RESET}"
    pause
    exit 1
fi

# ============================================================
# Load saves
# ============================================================

mapfile -t SAVES < <(
    find "$EXPORTS" -maxdepth 1 -type f -printf '%f\n' |
    sort -r
)

TOTAL=${#SAVES[@]}
PER_PAGE=9
PAGE=1

# ============================================================
# Show menu
# ============================================================

show_menu() {
    clear_screen

    echo
    echo -e "${WHITE}==============================================${RESET}"
    echo -e "${WHITE}     AVAILABLE SAVES FROM NEWEST TO OLDEST    ${RESET}"
    echo -e "${WHITE}==============================================${RESET}"
    echo
    echo -e "${YELLOW}Select a workspace to load or delete a save${RESET}"
    echo

    if [ "$TOTAL" -eq 0 ]; then
        echo -e " Page 1 (no saves)"
    else
        START=$(( (PAGE - 1) * PER_PAGE ))
        END=$(( START + PER_PAGE ))

        if [ "$END" -gt "$TOTAL" ]; then
            END=$TOTAL
        fi

        echo -e " Page $PAGE ($((START + 1)) - $END of $TOTAL)"
    fi

    echo

    echo -e "  ${GREEN}0. Run empty workspace${RESET}"

    if [ "$TOTAL" -gt 0 ]; then
        START=$(( (PAGE - 1) * PER_PAGE ))
        END=$(( START + PER_PAGE ))

        if [ "$END" -gt "$TOTAL" ]; then
            END=$TOTAL
        fi

        for ((i=START; i<END; i++)); do
            SLOT=$((i - START + 1))
            echo "  $SLOT. ${SAVES[$i]}"
        done
    fi

    echo
    echo -e "  ${YELLOW}q. Quit${RESET}"
    echo -e "  ${RED}d <number>     Delete save${RESET}"
    echo -e "  ${RED}d <n1,n2,n3>   Delete multiple saves${RESET}"
    echo -e "  ${RED}da             Delete all saves${RESET}"

    if [ "$TOTAL" -gt "$PER_PAGE" ]; then
        echo
        echo -e "  ${YELLOW}n = next page    p = previous page${RESET}"
    fi

    echo
}

# ============================================================
# Reload saves
# ============================================================

reload_saves() {
    SAVES=()

    while IFS= read -r file; do
        SAVES+=("$file")
    done < <(
        find "$EXPORTS" -maxdepth 1 -type f -printf '%f\n' |
        sort -r
    )

    TOTAL=${#SAVES[@]}
}

# ============================================================
# Save selection
# ============================================================

while true; do

    reload_saves
    show_menu

    read -rp "Select option: " CHOICE

    # Empty choice with no saves = workspace 0
    if [ "$TOTAL" -eq 0 ] && [ -z "$CHOICE" ]; then
        CHOICE="0"
    fi

    # ========================================================
    # Delete all
    # ========================================================

    if [ "$CHOICE" = "da" ]; then
        echo
        echo -e "${RED}Deleting ALL saves...${RESET}"

        find "$EXPORTS" -maxdepth 1 -type f -delete

        reload_saves
        continue
    fi

    # ========================================================
    # Delete selected saves
    # ========================================================

    if [[ "$CHOICE" =~ ^d[[:space:]]+(.+)$ ]]; then

        NUMBERS="${BASH_REMATCH[1]}"

        IFS=',' read -ra ITEMS <<< "$NUMBERS"

        for N in "${ITEMS[@]}"; do

            N="$(echo "$N" | xargs)"

            if ! [[ "$N" =~ ^[0-9]+$ ]]; then
                continue
            fi

            GLOBAL=$(( (PAGE - 1) * PER_PAGE + N - 1 ))

            if [ "$GLOBAL" -ge 0 ] && [ "$GLOBAL" -lt "$TOTAL" ]; then

                TARGET="${SAVES[$GLOBAL]}"
                TARGET_PATH="$EXPORTS/$TARGET"

                echo -e "${RED}Deleting save: $TARGET${RESET}"

                rm -f "$TARGET_PATH"
            fi
        done

        reload_saves
        continue
    fi

    # ========================================================
    # Empty workspace
    # ========================================================

    if [ "$CHOICE" = "0" ] || [ -z "$CHOICE" ]; then
        break
    fi

    # ========================================================
    # Next page
    # ========================================================

    if [ "$CHOICE" = "n" ]; then

        MAX_PAGE=$(( (TOTAL + PER_PAGE - 1) / PER_PAGE ))

        if [ "$PAGE" -lt "$MAX_PAGE" ]; then
            PAGE=$((PAGE + 1))
        fi

        continue
    fi

    # ========================================================
    # Previous page
    # ========================================================

    if [ "$CHOICE" = "p" ]; then

        if [ "$PAGE" -gt 1 ]; then
            PAGE=$((PAGE - 1))
        fi

        continue
    fi

    # ========================================================
    # Select save
    # ========================================================

    if [[ "$CHOICE" =~ ^[1-9]$ ]]; then

        GLOBAL=$(( (PAGE - 1) * PER_PAGE + CHOICE - 1 ))

        if [ "$GLOBAL" -lt "$TOTAL" ]; then

            SELECTED="${SAVES[$GLOBAL]}"
            SELECTED_PATH="$EXPORTS/$SELECTED"

            echo
            echo -e "${CYAN}Selected: $SELECTED${RESET}"

            # Copy save into container workspace
            cp "$SELECTED_PATH" "$DEST/"

            pushd "$DEST" >/dev/null

            case "$SELECTED" in

                *.zip)
                    unzip -o "$SELECTED"
                    ;;

                *.tar)
                    tar -xf "$SELECTED"
                    ;;

                *.tar.gz|*.tgz)
                    tar -xzf "$SELECTED"
                    ;;

                *)
                    echo -e "${RED}ERROR: Unsupported archive format.${RESET}"
                    popd >/dev/null
                    pause
                    exit 1
                    ;;
            esac

            rm -f "$SELECTED"

            popd >/dev/null

            break
        fi
    fi

    # ========================================================
    # Quit
    # ========================================================

    if [ "$CHOICE" = "q" ]; then

        display_delay "Preparing closing" 0.25

        clear_screen
        exit 0
    fi

done

# ============================================================
# Start Docker
# ============================================================

display_delay "Preparing the installation" 0.25

clear_screen

echo
echo -e "${CYAN}Building Docker image...${RESET}"

docker build -t "$IMAGE" "$SCRIPT_DIR"

clear_screen

echo
echo -e "${CYAN}Running container...${RESET}"

cd "$SCRIPT_DIR"

docker compose run --rm fm

# ============================================================
# Cleanup
# ============================================================

display_delay "Preparing Cleaning" 0.25

clear_screen

echo
read -rp "Execution finished. Press Enter to clean workspace and exit."

# ============================================================
# Clean workspace
# ============================================================

echo
echo -e "${CYAN}Cleaning workspace...${RESET}"

find "$DEST" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

read -rp "Workspace cleaned. Press Enter to continue."

# ============================================================
# Remove Docker image
# ============================================================

echo
echo -e "${CYAN}Cleaning Docker image...${RESET}"

docker image rm "$IMAGE" -f 2>/dev/null || true

read -rp "Docker image removed. Press Enter to continue."

# ============================================================
# Dangling images
# ============================================================

echo
echo -e "${CYAN}Cleaning dangling Docker images...${RESET}"

DANGLING=$(docker images -f "dangling=true" -q)

if [ -n "$DANGLING" ]; then
    docker rmi $DANGLING -f
    read -rp "Dangling images removed. Press Enter to continue."
else
    echo -e "${GREEN}No dangling images found.${RESET}"
    read -rp "Press Enter to continue."
fi

# ============================================================
# Unused volumes
# ============================================================

echo
echo -e "${CYAN}Cleaning unused Docker volumes...${RESET}"

VOLUMES=$(docker volume ls -qf "dangling=true")

if [ -n "$VOLUMES" ]; then
    docker volume rm $VOLUMES
    read -rp "Unused volumes removed. Press Enter to continue."
else
    echo -e "${GREEN}No unused volumes found.${RESET}"
    read -rp "Press Enter to continue."
fi

# ============================================================
# Unused networks
# ============================================================

echo
echo -e "${CYAN}Cleaning unused Docker networks...${RESET}"

NETWORKS=$(docker network ls -qf "dangling=true")

if [ -n "$NETWORKS" ]; then
    docker network rm $NETWORKS
    read -rp "Unused networks removed. Press Enter to continue."
else
    echo -e "${GREEN}No unused networks found.${RESET}"
    read -rp "Press Enter to continue."
fi

# ============================================================
# Stopped containers
# ============================================================

echo
echo -e "${CYAN}Cleaning stopped containers...${RESET}"

CONTAINERS=$(docker ps -a -q -f "status=exited")

if [ -n "$CONTAINERS" ]; then
    docker rm $CONTAINERS -f
    read -rp "Stopped containers removed. Press Enter to continue."
else
    echo -e "${GREEN}No stopped containers found.${RESET}"
    read -rp "Press Enter to continue."
fi

# ============================================================
# Build cache
# ============================================================

echo
echo -e "${CYAN}Cleaning build cache...${RESET}"

docker builder prune -f

read -rp "Build cache cleaned. Press Enter to continue."

# ============================================================
# Finished
# ============================================================

echo
echo -e "${GREEN}All cleanup operations completed.${RESET}"

read -rp "Press Enter to exit."

clear_screen