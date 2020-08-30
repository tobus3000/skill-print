Feature: linefeed
  Scenario: enable linefeed
    Given an English speaking user
     When the user says "enable linefeed"
     Then "skill-print.tobus3000" should reply with "Enabling linefeed."
  Scenario: disable linefeed
    Given an English speaking user
     When the user says "disable linefeed"
     Then "skill-print.tobus3000" should reply with "Disabling linefeed."