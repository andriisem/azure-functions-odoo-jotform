#!/bin/bash

REPO="andriisem/jotform-to-odoo"
VERSION="latest"

RED='\033[0;31m'
GRN='\033[0;32m'
PRP='\033[0;35m'
NC='\033[0m'

APP_NAME="odoojotformapp"
RESOURCE_GROUP="odooapr"
LOCATION="westeurope"
STORAGE_NAME="odooapps"
PREMIUM_PLAN="odooappp"

IMAGE_NAME=${REPO}:${VERSION}

if [[ $1 == "init" ]]; then
echo $RESOURCE_GROUP
    echo -e "${PRP}Create a resource group${NC}"
    az group create --name ${RESOURCE_GROUP} --location ${LOCATION}
    echo -e "${PRP}Create an Azure Storage account${NC}"
    az storage account create --name ${STORAGE_NAME} --location ${LOCATION} --resource-group ${RESOURCE_GROUP} --sku Standard_LRS
    echo -e "${PRP}Create a Premium plan${NC}"
    az functionapp plan create --resource-group ${RESOURCE_GROUP} --name ${PREMIUM_PLAN} --location ${LOCATION} --number-of-workers 1 --sku EP1 --is-linux
    echo -e "${PRP}Create an app from the image: ${NC}" ${IMAGE_NAME}
    az functionapp create --name ${APP_NAME} --storage-account  ${STORAGE_NAME}  --resource-group ${RESOURCE_GROUP} --plan ${PREMIUM_PLAN} --deployment-container-image-name ${IMAGE_NAME}
    echo -e "${GRN}Deploy successful${NC}"
fi

if [[ $1 == "updatefunction" ]]; then
    echo -e "${PRP}Rebuild function${NC}"
    docker rmi ${IMAGE_NAME}
    docker build -t ${IMAGE_NAME} .
    docker push ${IMAGE_NAME}
    echo -e "${PRP}Update function${NC}"
    az functionapp create --name ${APP_NAME} --storage-account  ${STORAGE_NAME}  --resource-group ${RESOURCE_GROUP} --plan ${PREMIUM_PLAN} --deployment-container-image-name ${IMAGE_NAME}
    echo -e "${GRN}Deploy successful${NC}"
    exit 0
fi
