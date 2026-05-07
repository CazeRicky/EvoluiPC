from django.core.management.base import BaseCommand
from core import neo4j_identity, neo4j_store


def _run_one(query, **params):
    """Execute a single Neo4j query and return a single result."""
    with neo4j_store.get_driver() as driver:
        with driver.session(database=neo4j_store.NEO4J_DATABASE) as session:
            return session.run(query, **params).single()


class Command(BaseCommand):
    help = 'Seed demo users with random hardware configurations'

    def handle(self, *args, **options):
        demo_users = [
            {'username': 'david', 'password': 'daviddavid', 'email': 'david@example.com'},
            {'username': 'victor', 'password': 'victorvictor', 'email': 'victor@example.com'},
            {'username': 'carlos', 'password': 'carloscarlos', 'email': 'carlos@example.com'},
        ]

        for user_data in demo_users:
            username = user_data['username']
            password = user_data['password']
            email = user_data['email']

            # Create user identity in Neo4j (or skip if already exists)
            try:
                user_result = neo4j_identity.ensure_user_identity(username, email, password)
                user_id = user_result['id']
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created user: {username}')
                )
            except ValueError as e:
                # User already exists, get the user ID from the username
                self.stdout.write(
                    self.style.WARNING(f'⚠ User already exists: {username}')
                )
                # Query Neo4j to get the user ID for hardware assignment
                record = _run_one(
                    "MATCH (u:AppUser {username: $username}) RETURN u.user_id AS user_id",
                    username=username
                )
                if not record:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Could not find user: {username}')
                    )
                    continue
                user_id = record['user_id']

            # Create a mock user object for hardware assignment
            mock_user = type('User', (), {'id': user_id, 'username': username, 'email': email})()

            # Assign random PC profile
            try:
                profile = neo4j_store.assign_random_pc_to_user(
                    user=mock_user,
                    source='neo4j-random-seed'
                )
                if profile:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Assigned PC profile to {username}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ No PC profile available for {username}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error assigning PC to {username}: {str(e)}')
                )

        # Seed hardware data for recommendations
        self._seed_hardware()

        self.stdout.write(
            self.style.SUCCESS('✓ Seed complete')
        )

    def _seed_hardware(self):
        """Create hardware nodes and relationships for upgrade recommendations."""
        self.stdout.write("\n📦 Seeding hardware data...")
        
        with neo4j_store.get_driver() as driver:
            with driver.session(database=neo4j_store.NEO4J_DATABASE) as session:
                # Check if hardware already exists
                exists = session.run("MATCH (m:Motherboard {name: 'A320M'}) RETURN COUNT(m) as count").single()
                if exists['count'] > 0:
                    self.stdout.write(self.style.WARNING('⚠ Hardware already exists, skipping'))
                    return

                try:
                    # Create sockets
                    session.run("""
                        CREATE (s1:Socket {name: "LGA1700"})
                    """)

                    # Create motherboard with socket
                    session.run("""
                        MATCH (s:Socket {name: "LGA1700"})
                        CREATE (mb:Motherboard {name: "A320M", socket: "LGA1700"})
                        CREATE (mb)-[:HAS_SOCKET]->(s)
                    """)

                    # Create processors with different performance levels
                    session.run("""
                        MATCH (s:Socket {name: "LGA1700"})
                        CREATE (cpu1:Processor {name: "Intel i5-10400", performance_score: 4500, price: 450.00, socket: "LGA1700"})
                        CREATE (cpu1)-[:FITS_IN]->(s)
                        
                        CREATE (cpu2:Processor {name: "Intel i5-12400", performance_score: 6500, price: 650.00, socket: "LGA1700"})
                        CREATE (cpu2)-[:FITS_IN]->(s)
                        
                        CREATE (cpu3:Processor {name: "Intel i7-13700K", performance_score: 9500, price: 1200.00, socket: "LGA1700"})
                        CREATE (cpu3)-[:FITS_IN]->(s)
                    """)

                    self.stdout.write(self.style.SUCCESS('✓ Hardware seed complete'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠ Hardware seed error: {str(e)}'))


