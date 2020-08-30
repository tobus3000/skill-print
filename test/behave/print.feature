Feature: print
  Scenario: print status
    Given an English speaking user
     When the user says "printer status"
     Then "skill-print.tobus3000" should reply with dialog from "status.dialog"
  Scenario: print time
    Given an English speaking user
     When the user says "print time"
     Then "skill-print.tobus3000" should reply with anything