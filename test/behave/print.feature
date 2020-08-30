Feature: print
  Scenario: print status
    Given an English speaking user
     When the user says "printer status"
     Then mycroft reply should contain "status"
  Scenario: print time
    Given an English speaking user
     When the user says "print time"
     Then "skill-print.tobus3000" should reply with anything