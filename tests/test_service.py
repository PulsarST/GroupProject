from tests.config import *

class TestGetters:

    @pytest.mark.asyncio
    async def test_get_zones(self):
        db = await get_test_db().__anext__()
        
        result = await get_zones(db)

        expected = {
            'id': ['A','B','C'],
            'name': ['Zone A','Zone B','Zone C'],
        }
        
        await db.aclose()

        assert compare_sequence(result, expected)

    @pytest.mark.asyncio
    async def test_get_spots(self):
        db = await get_test_db().__anext__()
        
        zone_id = 'B'
        result = await get_spots(db, zone_id)

        expected = {
            'id': [i for i in range(7,13)],
            'zone_id': [zone_id for i in range(6)],
            'type': [
                'unavailable',
                'standard',
                'standard',
                'accessible',
                'standard',
                'truck',
            ],
            'status': [
                'occupied',
                'available',
                'available',
                'available',
                'occupied',
                'available',
            ],
        }
        
        await db.aclose()

        assert compare_sequence(result, expected)

    @pytest.mark.asyncio
    async def test_get_sessions(self):
        db = await get_test_db().__anext__()
        
        zone_id = 'B'
        result = await get_sessions(db)

        expected = {
            'id': [i for i in range(1,11)],
            'zone_id': [
                'C','A','C',
                'B','C','A',
                'A','C','B','A'
                ],
            'spot_id': [
                13, 2, 14,
                11, 18, 4,
                5, 17, 7, 3
            ],
            'plate': [
                'М111ММ777',
                'Т123ТТ777',
                'Е001КХ750',
                'У333НН777',
                'О888ОО777',
                'Т000ТТ777',
                'А123ВС777',
                'М111ММ777',
                'О777ОО177',
                'H347GI341',
            ],
            'tariff_id': [1 for i in range(10)],
            'status': [
                'active',
                'active',
                'active',
                'active',
                'completed',
                'active',
                'active',
                'active',
                'active',
                'completed',
            ]
        }
        
        await db.aclose()

        assert compare_sequence(result, expected)

    @pytest.mark.asyncio
    async def test_get_payments(self):
        db = await get_test_db().__anext__()
        
        result = await get_payments(db)
        expected = {
            'id': [1],
            'session_id': [5],
            'amount': [150],
        }
        
        await db.aclose()

        assert compare_sequence(result, expected)

    @pytest.mark.asyncio
    async def test_iter_all_sessions(self):
        db = await get_test_db().__anext__()

        expected = {
            'id': [
                'C', 'A', 'C', 'B', 'C',
            ],
            'spot_id': [
                13, 2, 14, 11, 18,
            ],
        }

        result = []
        for i in range(5):
            result.append(await anext(iter_all_sessions(db)))

        return compare_sequence(result, expected)
    
    @pytest.mark.asyncio
    async def test_iter_active_sessions(self):
        db = await get_test_db().__anext__()

        expected = {
            'id': [
                'C', 'A', 'C', 'B', 'A',
            ],
            'spot_id': [
                13, 2, 14, 11, 4,
            ],
        }

        result = []
        for i in range(5):
            result.append(await anext(iter_active_sessions(db)))

        return compare_sequence(result, expected)

    @pytest.mark.asyncio
    async def test_get_endtime_sessions(self):
        db = await get_test_db().__anext__()

        expected = [
            "Session is not completed",
            "Session is not completed",
            "Session is not completed",
            "Session is not completed",
            "2025-10-21 13:28:44.064512",
            "Session is not completed",
            "Session is not completed",
            "Session is not completed",
            "Session is not completed",
            "2025-10-21 12:28:44.064512",
        ]

        result = await get_endtime_sessions(db)

        return result == expected


class TestSessionManipulation:

    async def uncreate_session(self, db: AsyncSession, session_id: int):
        """Функция, обращающая действия функции
           create_session_db
        """
        await close_session_db(db, session_id)

        session = await db.get(Session, session_id)
        if not session:
            raise ValueError("Session not found")

        await db.delete(session)
        await db.commit()
        return session

    async def unclose_session(self, db: AsyncSession, session_id: int):
        """Функция обращающая действия функции close_session
        """
        session = await db.get(Session, session_id)
        if not session or session.status == SessionStatus.active:
            raise ValueError("Closed session not found")
        
        session.status = SessionStatus.active
        session.end_time = None

        spot = await db.get(Spot, session.spot_id)
        spot.status = "occupied"

        await db.commit()
        await db.refresh(session)
        return session
    
    @pytest.mark.asyncio
    async def test_create_session_successful(self):
        db = await get_test_db().__anext__()
        
        result = await create_session_db(db, 'A', 3, "SATANA666", 3)
        success = result != None

        if success:
            session_id = len(await get_sessions(db))
            await self.uncreate_session(db, session_id)

        await db.aclose()
        assert success

    @pytest.mark.asyncio
    async def test_create_session_invalid_zone_or_spot(self):
        db = await get_test_db().__anext__()

        result = None
        
        try:
            result = await create_session_db(db, 'A', 8, "SATANA666", 3)
        except ValueError:
            await db.aclose()
            assert True

    @pytest.mark.asyncio
    async def test_create_session_occupied_spot(self):
        db = await get_test_db().__anext__()
        
        try:
            result = await create_session_db(db, 'B', 11, "SATANA666", 3)
        except ValueError:
            await db.aclose()
            assert True

    @pytest.mark.asyncio
    async def test_close_session_success(self):
        db = await get_test_db().__anext__()
        
        try:
            await close_session_db(db, 6)
        except ValueError:
            await db.aclose()
            assert False
        finally:
            await self.unclose_session(db, 6)
            await db.aclose()
            assert True

    @pytest.mark.asyncio
    async def test_close_session_already_closed(self):
        db = await get_test_db().__anext__()
        
        try:
            await close_session_db(db, 10)
        except ValueError:
            await db.aclose()
            assert True

    @pytest.mark.asyncio
    async def test_close_session_invalid_id(self):
        db = await get_test_db().__anext__()
        
        try:
            await close_session_db(db, 24535635)
        except ValueError:
            await db.aclose()
            assert True

class TestPaymentManipulation:
    async def uncreate_payment(self, db: AsyncSession, session_id: int):
        result = await db.execute(select(Payment).where(Payment.session_id == session_id))
        payment = result.scalars().first()
        if not payment:
            raise ValueError("Payment does not exist. Nothing to delete")
        
        await db.delete(payment)
        await db.commit()
        return payment

    @pytest.mark.asyncio
    async def test_create_payment_success(self):
        db = await get_test_db().__anext__()
        
        result = await create_payment_db(db, 10)
        # result.
        success = result != None

        expected = {
            'session_id': 10,
            'amount': 100.0,
        }

        if success:
            await self.uncreate_payment(db, 10)

        await db.aclose()
        assert compare(result, expected)

    @pytest.mark.asyncio
    async def test_get_final_payment_amount(self):
        db = await get_test_db().__anext__()
        
        result = await get_final_payment_amount(db)

        assert result == 150