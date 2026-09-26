SHELL := /bin/bash
ROOT := $(CURDIR)

ifeq ($(shell docker info >/dev/null 2>&1 && echo yes),yes)
  COMPOSE := docker compose
else
  COMPOSE := sudo docker compose
endif

.PHONY: start stop clean logs status help

start:
	@$(ROOT)/scripts/compose-up.sh

stop:
	@$(ROOT)/scripts/compose-down.sh

clean:
	@$(ROOT)/scripts/clean_influx_data.sh

logs:
	@$(COMPOSE) logs -f

status:
	@$(COMPOSE) ps

help:
	@echo "make start   Ask for test unit and serial, then start the stack"
	@echo "make stop    Stop the stack, clean the latest CSV, and write charts"
	@echo "make status  Show whether each service is running"
	@echo "make logs    Follow container logs"
	@echo "make clean   Delete InfluxDB data"
	@echo "make help    Show this list"
