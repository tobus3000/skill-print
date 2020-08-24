Feature: linefeed
  Scenario: enable linefeed
    Given an English speaking user
     When the user says "enable linefeed"
     Then "skill-print" should reply with "Enabling linefeed."