<?php

use Bitrix\Main\Config\Option;
use Bitrix\Main\Context;
use Bitrix\Main\Loader;
use Bitrix\Main\Localization\Loc;
use Bitrix\Main\SiteTable;
use Vendor\Aiagent\Access\SiteAccessProfile;
use Vendor\Aiagent\Access\SiteAccessRepository;

require_once $_SERVER["DOCUMENT_ROOT"] . "/bitrix/modules/main/include/prolog_admin_before.php";

Loc::loadMessages(__FILE__);

$moduleId = "vendor.aiagent";
$request = Context::getCurrent()->getRequest();
global $APPLICATION, $USER;

if (!$USER->isAdmin()) {
    $APPLICATION->authForm(Loc::getMessage("VENDOR_AIAGENT_ACCESS_DENIED"));
}

if (!Loader::includeModule($moduleId)) {
    return;
}

$repository = new SiteAccessRepository();
$sites = [];
$siteResult = SiteTable::getList(["select" => ["LID", "NAME"], "order" => ["LID" => "ASC"]]);
while ($site = $siteResult->fetch()) {
    $sites[] = [
        "LID" => (string)$site["LID"],
        "NAME" => (string)$site["NAME"],
    ];
}

if ($request->isPost() && check_bitrix_sessid() && ($request->getPost("save") !== null || $request->getPost("apply") !== null)) {
    $secret = trim((string)$request->getPost("webhook_secret"));
    Option::set($moduleId, "webhook_secret", $secret);

    foreach ($sites as $site) {
        $siteId = $site["LID"];
        $iblocksRaw = (string)$request->getPost("allowed_iblocks_" . $siteId);
        $accessLevel = (string)$request->getPost("settings_access_" . $siteId);
        $prefixesRaw = (string)$request->getPost("allowed_prefixes_" . $siteId);

        $allowedIblocks = array_values(array_filter(array_map("intval", preg_split("/[\s,;]+/", $iblocksRaw) ?: [])));
        $allowedPrefixes = array_values(
            array_filter(
                array_map(
                    static function (string $prefix): string {
                        return trim($prefix);
                    },
                    preg_split("/[\r\n,;]+/", $prefixesRaw) ?: []
                )
            )
        );
        if (!in_array($accessLevel, ["none", "limited", "full"], true)) {
            $accessLevel = "none";
        }

        $repository->saveProfile(
            new SiteAccessProfile(
                $siteId,
                $allowedIblocks,
                $accessLevel,
                $allowedPrefixes
            )
        );
    }

    CAdminMessage::showMessage([
        "MESSAGE" => Loc::getMessage("VENDOR_AIAGENT_OPTIONS_SAVED"),
        "TYPE" => "OK",
    ]);
}

$profiles = $repository->getAllProfiles();
$webhookSecret = (string)Option::get($moduleId, "webhook_secret", "");

?>
<form method="post" action="<?= $APPLICATION->GetCurPage() ?>?mid=<?= htmlspecialcharsbx($moduleId) ?>&lang=<?= LANGUAGE_ID ?>">
    <?= bitrix_sessid_post() ?>
    <table class="adm-detail-content-table edit-table">
        <tbody>
            <tr class="heading">
                <td colspan="2"><?= Loc::getMessage("VENDOR_AIAGENT_WEBHOOK_SECTION") ?></td>
            </tr>
            <tr>
                <td width="50%"><?= Loc::getMessage("VENDOR_AIAGENT_WEBHOOK_SECRET") ?></td>
                <td width="50%">
                    <input type="text" size="60" name="webhook_secret" value="<?= htmlspecialcharsbx($webhookSecret) ?>" />
                </td>
            </tr>
            <tr class="heading">
                <td colspan="2"><?= Loc::getMessage("VENDOR_AIAGENT_SITES_SECTION") ?></td>
            </tr>
            <?php foreach ($sites as $site): ?>
                <?php
                $siteId = $site["LID"];
                $profile = $profiles[$siteId] ?? new SiteAccessProfile($siteId, [], "none", []);
                ?>
                <tr>
                    <td colspan="2">
                        <b><?= htmlspecialcharsbx($siteId . " — " . $site["NAME"]) ?></b>
                    </td>
                </tr>
                <tr>
                    <td><?= Loc::getMessage("VENDOR_AIAGENT_ALLOWED_IBLOCKS") ?></td>
                    <td>
                        <input
                            type="text"
                            size="60"
                            name="allowed_iblocks_<?= htmlspecialcharsbx($siteId) ?>"
                            value="<?= htmlspecialcharsbx(implode(",", $profile->getAllowedIblocks())) ?>"
                        />
                    </td>
                </tr>
                <tr>
                    <td><?= Loc::getMessage("VENDOR_AIAGENT_SETTINGS_ACCESS_LEVEL") ?></td>
                    <td>
                        <select name="settings_access_<?= htmlspecialcharsbx($siteId) ?>">
                            <?php
                            $levels = [
                                "none" => Loc::getMessage("VENDOR_AIAGENT_ACCESS_NONE"),
                                "limited" => Loc::getMessage("VENDOR_AIAGENT_ACCESS_LIMITED"),
                                "full" => Loc::getMessage("VENDOR_AIAGENT_ACCESS_FULL"),
                            ];
                            foreach ($levels as $levelKey => $label):
                                ?>
                                <option
                                    value="<?= htmlspecialcharsbx($levelKey) ?>"
                                    <?= $profile->getSettingsAccess() === $levelKey ? "selected" : "" ?>
                                >
                                    <?= htmlspecialcharsbx((string)$label) ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </td>
                </tr>
                <tr>
                    <td><?= Loc::getMessage("VENDOR_AIAGENT_ALLOWED_PREFIXES") ?></td>
                    <td>
                        <textarea
                            rows="3"
                            cols="60"
                            name="allowed_prefixes_<?= htmlspecialcharsbx($siteId) ?>"
                        ><?= htmlspecialcharsbx(implode(",", $profile->getAllowedSettingPrefixes())) ?></textarea>
                    </td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
    <div class="adm-detail-content-btns-wrap">
        <div class="adm-detail-content-btns">
            <input type="submit" name="save" value="<?= Loc::getMessage("VENDOR_AIAGENT_SAVE") ?>" class="adm-btn-save" />
            <input type="submit" name="apply" value="<?= Loc::getMessage("VENDOR_AIAGENT_APPLY") ?>" class="adm-btn" />
        </div>
    </div>
</form>
<?php

require_once $_SERVER["DOCUMENT_ROOT"] . "/bitrix/modules/main/include/epilog_admin.php";

