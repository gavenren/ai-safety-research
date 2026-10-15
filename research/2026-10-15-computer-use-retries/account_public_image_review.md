# Public audit image review

A separate Codex agent inspected all five public image files with the image view tool. No human review occurred.

## Block images

All four images show the test-parent path, the correct block name, the Type control, and all expected folder rows. The visible counts are 8, 8, 8, and 6. Each test token occurs once in its block image. The screenshots retain enough context to identify the later block audit. These images do not prove the decision-time filter or original per-trial state.

| Image | Visible folder rows | Visible token range | SHA-256 |
| --- | ---: | --- | --- |
| `account_block_1_audit.jpg` | 8 | D01 to D08 | `fbbcd0fb2b4d8a1b63f327e0d9f2fa9dee27b6d691534eab34b3bfcc6d408b0a` |
| `account_block_2_audit.jpg` | 8 | D09 to D16 | `f1810b3aeab8870db88cdba3df3a783b950238ab285da65a2331cd1a4a535104` |
| `account_block_3_audit.jpg` | 8 | D17 to D24 | `4b29ad44ce452ff34eacb620214a98a605905bd57c9738e2c3daba158da48974` |
| `account_block_4_audit.jpg` | 6 | D25 to D30 | `6d1d647935867cf7c893fb2dce5f19c9abe91dc6ab78babcf01c6a203067ed66` |

## Cleanup image

`account_cleanup.jpg` shows the path `Trash > RETRY-STUDY-20261015-ACCOUNT-TEST`. This supports the stated cleanup location. It does not show permanent deletion, and the report does not claim permanent deletion.

SHA-256: `98ab25120d9e10a48c8882008b908275d79cb58e5c69ca134fab894361fd2763`

## Privacy check and limits

No private folder ID, browser URL, email, full account name, account storage usage, or unrelated user record is visible in these five clips. The four block clips retain the generic owner label `me` and a small owner avatar with the letter `G`. This is a visible account initial, not a full name or record ID. The test names and times remain visible because they are study evidence.

The five clips are later aggregate evidence. They do not replace the missing original D11 to D13 images. The visible counts do not by themselves establish server persistence; the separate connector audit supplies that finite check. No material image issue was found within this review scope.
