import tomlkit
from dataclasses import dataclass, field


@dataclass
class Vault:
    name: str
    path: str
    tags: list[str] = field(default_factory=list)

@dataclass
class Settings:
    ai_endpoint: str
    ai_model: str
    ai_temp: float
    default_vault: str
    vaults: list[Vault] = field(default_factory=list)

    @classmethod
    def load(cls):
        with open ("config.toml", "rb") as f:
            data = tomlkit.load(f)

        vault_data = data.get("vaults", {})
        vaults = [Vault(**item) for item in vault_data.get("items", [])]
        return cls(
            ai_endpoint=data["ai"]["endpoint"],
            ai_model=data["ai"]["model"],
            ai_temp=data["ai"]["temperature"],
            default_vault=vault_data.get("default", ""),
            vaults=vaults
        )

    def get_vault(self, name: str) -> Vault | None:
        for vault in self.vaults:
            if vault.name == name:
                return vault
        return None

    def add_tag(self, tag: str, vault: Vault):
        for v in self.vaults:
            if v == vault:
                v.tags.append(tag)
                self.save()

    def add_vault(self, name: str, path: str):
        from obsidian import search_tags
        if self.get_vault(name):
            raise ValueError(f"Vault '{name}' already exists")
        new_vault = Vault(name=name, path=path)
        new_vault.tags = search_tags(new_vault)
        self.vaults.append(new_vault)

    def remove_vault(self, name: str):
        self.vaults = [v for v in self.vaults if v.name != name]

    def list_vaults(self):
        return [(v.name, v.path )for v in self.vaults]

    def save(self):
        with (open ("config.toml", "rb") as f):
            data = tomlkit.load(f)
            data["ai"]["endpoint"] = self.ai_endpoint
            data["ai"]["model"] = self.ai_model
            data["ai"]["temperature"] = self.ai_temp
            data["vaults"]["default"] = self.default_vault
            data["vaults"]["items"] = [
                {
                    "name": v.name,
                    "path": v.path,
                    "tags": v.tags,
                } for v in self.vaults
            ]
        with open ("config.toml", "w") as f:
            tomlkit.dump(data, f)
