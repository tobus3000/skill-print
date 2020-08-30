Feature: printer
  Scenario: printer status
    Given an English speaking user
     When the user says "printer status"
     Then "skill-print.tobus3000" should reply with dialog from "status.dialog"
  Scenario: disable printer
    Given an English speaking user
     When the user says "disable printer"
     Then "skill-print.tobus3000" should reply with dialog from "status.dialog"
  Scenario: enable printer
    Given an English speaking user
     When the user says "enable printer"
     Then "skill-print.tobus3000" should reply with dialog from "status.dialog"
  Scenario: turn printer off
    Given an English speaking user
     When the user says "Turn printer off"
     Then "skill-print.tobus3000" should reply with dialog from "status.dialog"
  Scenario: turn printer on
    Given an English speaking user
     When the user says "Turn printer on"
     Then "skill-print.tobus3000" should reply with dialog from "status.dialog"
  