#!/bin/bash
# Elasticsearch Index Template Management Script

ELASTICSEARCH_URL="http://localhost:9200"
TEMPLATE_FILE="logs-template.json"
TEMPLATE_NAME="logs-template"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function print_usage() {
    echo "Usage: $0 {create|update|delete|list|show|verify}"
    echo ""
    echo "Commands:"
    echo "  create  - Create the index template from $TEMPLATE_FILE"
    echo "  update  - Update the existing index template"
    echo "  delete  - Delete the index template"
    echo "  list    - List all index templates"
    echo "  show    - Show the current logs-template configuration"
    echo "  verify  - Verify template is applied to existing indices"
}

function create_template() {
    echo -e "${YELLOW}Creating index template '$TEMPLATE_NAME'...${NC}"
    
    if [ ! -f "$TEMPLATE_FILE" ]; then
        echo -e "${RED}Error: Template file '$TEMPLATE_FILE' not found!${NC}"
        exit 1
    fi
    
    response=$(curl -s -w "\n%{http_code}" -X PUT "$ELASTICSEARCH_URL/_index_template/$TEMPLATE_NAME" \
        -H 'Content-Type: application/json' \
        -d @"$TEMPLATE_FILE")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✓ Template created successfully!${NC}"
        echo "$body" | grep -q '"acknowledged":true' && echo -e "${GREEN}  Acknowledged by Elasticsearch${NC}"
    else
        echo -e "${RED}✗ Failed to create template (HTTP $http_code)${NC}"
        echo "$body"
        exit 1
    fi
}

function delete_template() {
    echo -e "${YELLOW}Deleting index template '$TEMPLATE_NAME'...${NC}"
    
    response=$(curl -s -w "\n%{http_code}" -X DELETE "$ELASTICSEARCH_URL/_index_template/$TEMPLATE_NAME")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✓ Template deleted successfully!${NC}"
    else
        echo -e "${RED}✗ Failed to delete template (HTTP $http_code)${NC}"
        echo "$body"
        exit 1
    fi
}

function list_templates() {
    echo -e "${YELLOW}Listing all index templates:${NC}"
    curl -s "$ELASTICSEARCH_URL/_cat/templates?v&s=name"
}

function show_template() {
    echo -e "${YELLOW}Showing template '$TEMPLATE_NAME':${NC}"
    curl -s "$ELASTICSEARCH_URL/_index_template/$TEMPLATE_NAME?pretty"
}

function verify_template() {
    echo -e "${YELLOW}Verifying template application to indices:${NC}"
    
    # Get all logstash indices
    indices=$(curl -s "$ELASTICSEARCH_URL/_cat/indices/logstash-*?h=index" | tr '\n' ' ')
    
    if [ -z "$indices" ]; then
        echo -e "${YELLOW}No logstash-* indices found.${NC}"
        return
    fi
    
    echo -e "${GREEN}Found indices: $indices${NC}"
    
    for index in $indices; do
        echo -e "\n${YELLOW}Checking mapping for: $index${NC}"
        
        # Check specific fields from template
        mapping=$(curl -s "$ELASTICSEARCH_URL/$index/_mapping")
        
        if echo "$mapping" | grep -q '"ip":{"type":"ip"}'; then
            echo -e "  ${GREEN}✓ ip field: correct type (ip)${NC}"
        else
            echo -e "  ${RED}✗ ip field: incorrect or missing${NC}"
        fi
        
        if echo "$mapping" | grep -q '"level":{"type":"keyword"'; then
            echo -e "  ${GREEN}✓ level field: correct type (keyword)${NC}"
        else
            echo -e "  ${RED}✗ level field: incorrect or missing${NC}"
        fi
        
        if echo "$mapping" | grep -q '"message":{"type":"text"'; then
            echo -e "  ${GREEN}✓ message field: correct type (text)${NC}"
        else
            echo -e "  ${RED}✗ message field: incorrect or missing${NC}"
        fi
        
        if echo "$mapping" | grep -q '"service":{"type":"keyword"'; then
            echo -e "  ${GREEN}✓ service field: correct type (keyword)${NC}"
        else
            echo -e "  ${RED}✗ service field: incorrect or missing${NC}"
        fi
    done
}

# Main script
case "$1" in
    create|update)
        create_template
        ;;
    delete)
        delete_template
        ;;
    list)
        list_templates
        ;;
    show)
        show_template
        ;;
    verify)
        verify_template
        ;;
    *)
        print_usage
        exit 1
        ;;
esac
