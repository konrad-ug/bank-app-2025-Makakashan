Feature: Account transfers

  Scenario: User is able to make incoming transfer
    Given Account registry is empty
    And I create an account using name: "john", last name: "doe", pesel: "85050512345"
    When I make an incoming transfer of "500.0" to account with pesel: "85050512345"
    Then Account with pesel "85050512345" has "balance" equal to "500.0"

  Scenario: User is able to make outgoing transfer with sufficient balance
    Given Account registry is empty
    And I create an account using name: "anna", last name: "smith", pesel: "90010112345"
    And I make an incoming transfer of "1000.0" to account with pesel: "90010112345"
    When I make an outgoing transfer of "300.0" from account with pesel: "90010112345"
    Then Account with pesel "90010112345" has "balance" equal to "700.0"

  Scenario: User cannot make outgoing transfer with insufficient balance
    Given Account registry is empty
    And I create an account using name: "bob", last name: "jones", pesel: "88030312345"
    And I make an incoming transfer of "100.0" to account with pesel: "88030312345"
    When I try to make an outgoing transfer of "200.0" from account with pesel: "88030312345"
    Then Transfer fails with status code "422"
    And Account with pesel "88030312345" has "balance" equal to "100.0"

  Scenario: User is able to make express transfer with fee
    Given Account registry is empty
    And I create an account using name: "kate", last name: "wilson", pesel: "92020212345"
    And I make an incoming transfer of "500.0" to account with pesel: "92020212345"
    When I make an express transfer of "100.0" from account with pesel: "92020212345"
    Then Account with pesel "92020212345" has "balance" equal to "399.0"

  Scenario: User can make multiple transfers
    Given Account registry is empty
    And I create an account using name: "mike", last name: "brown", pesel: "87070712345"
    When I make an incoming transfer of "1000.0" to account with pesel: "87070712345"
    And I make an outgoing transfer of "200.0" from account with pesel: "87070712345"
    And I make an incoming transfer of "500.0" to account with pesel: "87070712345"
    And I make an outgoing transfer of "100.0" from account with pesel: "87070712345"
    Then Account with pesel "87070712345" has "balance" equal to "1200.0"

  Scenario: Transfer to non-existent account fails
    Given Account registry is empty
    When I try to make an incoming transfer of "100.0" to account with pesel: "99999999999"
    Then Transfer fails with status code "404"

  Scenario: User cannot make express transfer with insufficient balance for amount plus fee
    Given Account registry is empty
    And I create an account using name: "sarah", last name: "davis", pesel: "91050512345"
    And I make an incoming transfer of "100.0" to account with pesel: "91050512345"
    When I try to make an express transfer of "100.0" from account with pesel: "91050512345"
    Then Transfer fails with status code "422"
    And Account with pesel "91050512345" has "balance" equal to "100.0"
