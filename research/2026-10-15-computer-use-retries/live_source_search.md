# Source search for the live website extension

Date: 2026-10-15. No source supports a claim that these rules are new. This search is limited. The two selected sites are public test apps, not production services.

## Searches before scored trials

1. site.arxiv.org browser agent real websites benchmark WebVoyager Online Mind2Web retry verification 2026
2. site.github.com realworld browser benchmark web tasks test accounts benchmark BrowserGym retry
3. UI testing playground official ajax button 15 seconds site:github.com
4. site:practice.expandtesting.com ajax dynamic loading add remove

## Read sources and use

- He et al. (2024), WebVoyager. https://aclanthology.org/2024.acl-long.371/ and https://aclanthology.org/2024.acl-long.371.pdf . Read the abstract and relevant method text on live website tasks. Use only to establish prior real-site agent evaluation. Do not transfer its success rate or task coverage to this study.
- Kara, Faisal, and Nath (2025), WAREX, arXiv:2510.03285v1, September 28. https://arxiv.org/html/2510.03285v1 . Read introduction, framework sections 3.1-3.5, experiment setup and result discussion. This is a preprint. It uses injected infrastructure failures. The present extension instead tests normal filtered-list behavior. No WAREX code or data were used.
- TodoMVC application specification. https://raw.githubusercontent.com/tastejs/todomvc/master/app-spec.md . Read creation, filtering, routing and persistence requirements. It specifies localStorage and the All/Active/Completed views. A specification does not prove the live site complies.
- TodoMVC home page. https://todomvc.com/ . Read purpose and listed demo links. The root used its links for React, Vue, and KnockoutJS feasibility checks.
- Microsoft Playwright documentation. https://playwright.dev/docs/codegen and https://playwright.dev/docs/writing-tests . Read the demo use and UI test examples. The codegen guide uses https://demo.playwright.dev/todomvc/ . This supports a small test through normal controls. No browser-network interception or private accounts were used.
- TodoMVC license. https://raw.githubusercontent.com/tastejs/todomvc/master/license.md . The reviewer checked source attribution. No third-party application source is bundled. Screenshots show small test-app views and synthetic tasks as evidence, with attribution to their source sites. Do not assign the Playwright framework license to all demo assets.
- NeurIPS Paper Checklist Guidelines. https://neurips.cc/public/guides/PaperChecklist . Read claims, limitations, theory, reproducibility, open data/code, experimental details, compute, ethics, safeguards and licenses. Used as a review aid, not as a claim of approval.

The separate design reviewer checked the served app sources and saved hashes in live_design_review.md. The trial agents did not read those sources. The source check found a 500 ms rate limit in KnockoutJS storage writes; no general persistence bound is inferred from it.

## Access and selection failures

OpenReview's proposed Online Mind2Web paper link led to a browser verification page; the full paper was not read and is not cited. UI Testing Playground HTTPS failed a certificate check in the browser and was excluded. No browser warning was bypassed. A design reviewer read its advertised HTTP source; no scored trial used it. React and Vue lost their warm-up task after reload. KnockoutJS initially had an unready input action, then passed a separate warm-up. See live_preflight.md. These choices select working test apps and limit generality.

## Proposed contribution

The study adds a saved comparison of five supplied retry procedures under All and Completed views. A fresh but partial view can omit a completed create action. The additional scope check tests one direct response to that cause. This is an application of known filtering and reconciliation ideas. It is not a new general protocol, field error estimate, autonomous benchmark score, or proof of production safety.
