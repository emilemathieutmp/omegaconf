from omegaconf import DictConfig, ListConfig, OmegaConf


class TestGetFullKey:
    # 1
    def test_dict(self) -> None:
        c = OmegaConf.create(dict(a=1))
        assert isinstance(c, DictConfig)
        assert c.get_full_key("a") == "a"

    def test_list(self) -> None:
        c = OmegaConf.create([1, 2, 3])
        assert isinstance(c, ListConfig)
        assert c.get_full_key("2") == "[2]"

    # 2
    def test_dd(self) -> None:
        c = OmegaConf.create(dict(a=1, b=dict(c=1)))
        assert isinstance(c, DictConfig)
        assert c.b.get_full_key("c") == "b.c"

    def test_dl(self) -> None:
        c = OmegaConf.create(dict(a=[1, 2, 3]))
        assert isinstance(c, DictConfig)
        assert c.a.get_full_key(1) == "a[1]"

    def test_ll(self) -> None:
        c = OmegaConf.create([[1, 2, 3]])
        assert isinstance(c, ListConfig)
        assert c[0].get_full_key("2") == "[0][2]"

    def test_ld(self) -> None:
        c = OmegaConf.create([1, 2, dict(a=1)])
        assert isinstance(c, ListConfig)
        assert c[2].get_full_key("a") == "[2].a"

    # 3
    def test_ddd(self) -> None:
        c = OmegaConf.create(dict(a=dict(b=dict(c=1))))
        assert isinstance(c, DictConfig)
        assert c.a.b.get_full_key("c") == "a.b.c"

    def test_ddl(self) -> None:
        c = OmegaConf.create(dict(a=dict(b=[0, 1])))
        assert c.a.b.get_full_key(0) == "a.b[0]"

    def test_dll(self) -> None:
        c = OmegaConf.create(dict(a=[1, [2]]))
        assert c.a[1].get_full_key(0) == "a[1][0]"

    def test_dld(self) -> None:
        c = OmegaConf.create(dict(a=[dict(b=2)]))
        assert c.a[0].get_full_key("b") == "a[0].b"

    def test_ldd(self) -> None:
        c = OmegaConf.create([dict(a=dict(b=1))])
        assert isinstance(c, ListConfig)
        assert c[0].a.get_full_key("b") == "[0].a.b"

    def test_ldl(self) -> None:
        c = OmegaConf.create([dict(a=[0])])
        assert isinstance(c, ListConfig)
        assert c[0].a.get_full_key(0) == "[0].a[0]"

    def test_lll(self) -> None:
        c = OmegaConf.create([[[0]]])
        assert isinstance(c, ListConfig)
        assert c[0][0].get_full_key(0) == "[0][0][0]"

    def test_lld(self) -> None:
        c = OmegaConf.create([[dict(a=1)]])
        assert isinstance(c, ListConfig)
        assert c[0][0].get_full_key("a") == "[0][0].a"

    def test_lldddl(self) -> None:
        c = OmegaConf.create([[dict(a=dict(a=[0]))]])
        assert isinstance(c, ListConfig)
        assert c[0][0].a.a.get_full_key(0) == "[0][0].a.a[0]"

    # special cases
    def test_parent_with_missing_item(self) -> None:
        c = OmegaConf.create(dict(x="???", a=1, b=dict(c=1)))
        assert isinstance(c, DictConfig)
        assert c.b.get_full_key("c") == "b.c"
