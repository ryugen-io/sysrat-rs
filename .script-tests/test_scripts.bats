#!/usr/bin/env bats
# BATS tests for Config Manager shell scripts
# Temporary test file - not committed to repository

# Test lines.sh
@test "lines.sh: syntax is valid" {
    bash -n lines.sh
}

@test "lines.sh: is executable" {
    [ -x lines.sh ]
}

@test "lines.sh: runs without errors" {
    run ./lines.sh 200
    [ "$status" -eq 0 ]
}

@test "lines.sh: shows summary" {
    run ./lines.sh 200
    [[ "$output" =~ "Summary:" ]]
}

@test "lines.sh: counts files" {
    run ./lines.sh 200
    [[ "$output" =~ "Total files:" ]]
}

@test "lines.sh: accepts custom limit" {
    run ./lines.sh 100
    [[ "$output" =~ "limit: 100 lines" ]]
}

# Test lint.sh
@test "lint.sh: syntax is valid" {
    bash -n lint.sh
}

@test "lint.sh: is executable" {
    [ -x lint.sh ]
}

@test "lint.sh: runs without errors" {
    run ./lint.sh
    # May fail if issues found, that's OK
    [ "$status" -eq 0 ] || [ "$status" -eq 1 ]
}

# Test rebuild.sh
@test "rebuild.sh: syntax is valid" {
    bash -n rebuild.sh
}

@test "rebuild.sh: is executable" {
    [ -x rebuild.sh ]
}

@test "rebuild.sh: shows help" {
    run ./rebuild.sh --help
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage:" ]]
}

# Test start.sh
@test "start.sh: syntax is valid" {
    bash -n start.sh
}

@test "start.sh: is executable" {
    [ -x start.sh ]
}

# Test stop.sh
@test "stop.sh: syntax is valid" {
    bash -n stop.sh
}

@test "stop.sh: is executable" {
    [ -x stop.sh ]
}

# Integration test
@test "all shell scripts have proper shebangs" {
    for script in *.sh; do
        head -n 1 "$script" | grep -q "^#!/"
    done
}

@test "all shell scripts use set -e" {
    for script in *.sh; do
        grep -q "set -e" "$script" || grep -q "set -o errexit" "$script"
    done
}
