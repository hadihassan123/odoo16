/** @odoo-module */
import { registry } from "@web/core/registry"
import { KpiCard } from "./kpi_card/kpi_card"
const { Component } = amc_management

export class OwlSalesDashboard.template = "amc_management.OwlSalesDashboard"

OwlSalesDashboard.template = "amc_management.OwlSalesDashboard"
OwlSalesDashboard.components = {KpiCard}

registry.category("actions").add("amc_management.sales_dashboard",OwlSalesDashboard)