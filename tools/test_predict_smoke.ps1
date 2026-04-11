# =============================================================================
# test_predict_smoke.ps1
#
# AOI Defect Triage v1 — Phase 2 API Smoke Test
#
# Runs two tests against the running FastAPI service at http://127.0.0.1:8000:
#   Test 1 (Happy Path)   — sends a real wafer image and checks all contract fields
#   Test 2 (Bad Request)  — sends invalid base64 and verifies the API rejects it
#
# Usage (from project root):
#   .\tools\test_predict_smoke.ps1
#
# Prerequisites:
#   - API must already be running:
#       uvicorn src.api:app --reload
#   - PowerShell 5.1+ (built into Windows 10/11)
# =============================================================================

$ErrorActionPreference = "Stop"

$API_URL    = "http://127.0.0.1:8000/predict"
$IMAGE_PATH = "data\processed\test\Scratch\test_000561.png"

# Required fields in a valid response (locked AOI contract + Phase 2 metadata)
$REQUIRED_FIELDS = @(
    "image_id",
    "machine_id",
    "lot_id",
    "layer",
    "timestamp",
    "defect_class",
    "confidence",
    "bbox",
    "ng_flag",
    "model_name",
    "model_version",
    "request_id",
    "processing_time_ms",
    "schema_version"
)

$passCount = 0
$failCount = 0

function Write-Pass($msg) {
    Write-Host "  [PASS] $msg" -ForegroundColor Green
}
function Write-Fail($msg) {
    Write-Host "  [FAIL] $msg" -ForegroundColor Red
}
function Write-Header($msg) {
    Write-Host ""
    Write-Host "--------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  $msg" -ForegroundColor Cyan
    Write-Host "--------------------------------------------------------------" -ForegroundColor Cyan
}

# =============================================================================
# Test 1 — Happy Path
# =============================================================================
Write-Header "Test 1: Happy Path  (valid Scratch image -> /predict)"

# --- check image file exists ---
if (-not (Test-Path $IMAGE_PATH)) {
    Write-Fail "Sample image not found: $IMAGE_PATH"
    Write-Host "  Make sure you have run prepare_data.py and the test split exists." -ForegroundColor Yellow
    $failCount++
} else {

    # --- encode image to base64 ---
    $imageBytes   = [System.IO.File]::ReadAllBytes((Resolve-Path $IMAGE_PATH))
    $imageBase64  = [System.Convert]::ToBase64String($imageBytes)

    $body = @{
        image_base64 = $imageBase64
        image_id     = "smoke_test_001"
        machine_id   = "AOI_SMOKE"
        lot_id       = "LOT_SMOKE"
        layer        = "ILD"
    } | ConvertTo-Json

    # --- call the API ---
    try {
        $response = Invoke-RestMethod `
            -Method Post `
            -Uri $API_URL `
            -ContentType "application/json" `
            -Body $body

        Write-Host ""
        Write-Host "  Full response:" -ForegroundColor White
        Write-Host ($response | ConvertTo-Json -Depth 5) -ForegroundColor Gray

        # --- field checks ---
        Write-Host ""
        Write-Host "  Checking required fields:" -ForegroundColor White
        $allFieldsPresent = $true
        foreach ($field in $REQUIRED_FIELDS) {
            $value = $response.PSObject.Properties[$field]
            if ($null -eq $value) {
                Write-Fail "Missing field: $field"
                $allFieldsPresent = $false
                $failCount++
            } else {
                Write-Host "    OK  $field = $($value.Value)" -ForegroundColor DarkGreen
            }
        }

        if ($allFieldsPresent) {
            Write-Host ""
            Write-Pass "All 14 contract fields present"
            $passCount++
        }

    } catch {
        Write-Fail "HTTP request failed: $_"
        Write-Host "  Is the API running?  Run: uvicorn src.api:app --reload" -ForegroundColor Yellow
        $failCount++
    }
}

# =============================================================================
# Test 2 — Bad Request (invalid base64)
# =============================================================================
Write-Header "Test 2: Bad Request  (invalid base64 -> expect HTTP 400)"

$badBody = @{
    image_base64 = "THIS_IS_NOT_VALID_BASE64_!!!"
    image_id     = "smoke_bad_001"
} | ConvertTo-Json

try {
    # Invoke-RestMethod throws on 4xx; catch and inspect the response
    $badResponse = Invoke-RestMethod `
        -Method Post `
        -Uri $API_URL `
        -ContentType "application/json" `
        -Body $badBody

    # If we reach here the API did NOT reject the bad input — that is a failure
    Write-Host ""
    Write-Host "  Unexpected success response:" -ForegroundColor Yellow
    Write-Host ($badResponse | ConvertTo-Json -Depth 5) -ForegroundColor Gray
    Write-Fail "API accepted invalid base64 — expected HTTP 400"
    $failCount++

} catch {
    # PowerShell wraps the HTTP error; extract the response body
    $statusCode   = $null
    $errorContent = $null

    if ($_.Exception.Response) {
        $statusCode = [int]$_.Exception.Response.StatusCode

        # Read the body from the error stream
        $stream = $_.Exception.Response.GetResponseStream()
        if ($stream) {
            $reader      = New-Object System.IO.StreamReader($stream)
            $errorContent = $reader.ReadToEnd()
            $reader.Close()
        }
    }

    Write-Host ""
    Write-Host "  HTTP status: $statusCode" -ForegroundColor White
    if ($errorContent) {
        Write-Host "  Error body:  $errorContent" -ForegroundColor Gray
    }

    if ($statusCode -eq 400) {
        Write-Pass "API correctly returned HTTP 400 for invalid base64"
        $passCount++
    } elseif ($null -eq $statusCode) {
        Write-Fail "Could not reach API: $_"
        Write-Host "  Is the API running?  Run: uvicorn src.api:app --reload" -ForegroundColor Yellow
        $failCount++
    } else {
        Write-Fail "Expected HTTP 400, got HTTP $statusCode"
        $failCount++
    }
}

# =============================================================================
# Summary
# =============================================================================
Write-Header "Smoke Test Summary"
Write-Host "  PASS: $passCount" -ForegroundColor Green
Write-Host "  FAIL: $failCount" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Red" })
Write-Host ""
if ($failCount -eq 0) {
    Write-Host "  ALL TESTS PASSED — Phase 2 API is healthy." -ForegroundColor Green
} else {
    Write-Host "  ONE OR MORE TESTS FAILED — check output above." -ForegroundColor Red
}
Write-Host ""
