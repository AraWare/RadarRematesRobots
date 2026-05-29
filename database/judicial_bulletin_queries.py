from auction import Auction
from bulletin_auction import BulletinAuction
from database.database_connection import connection

def insert_bulletin_auctions(auctions: list[Auction], bulletin_search_id: str):

    cursor = connection.cursor()
    query = """
        INSERT INTO [ThirdParties].[BulletinAuctions] (
            [BulletinAuctionId],
            [AuctionReferenceNumber],
            [Auction],
            [JudicialBulletinId]
        )
        SELECT
            ISNULL((SELECT MAX([BulletinAuctionId]) FROM [ThirdParties].[BulletinAuctions]), 0) + 1,
            converted_auction.AuctionReferenceNumber,
            ?,
            judicial_bulletin.JudicialBulletinId
        FROM [ThirdParties].[JudicialBulletins] AS judicial_bulletin
        CROSS APPLY (SELECT TRY_CONVERT(INT, ?) AS AuctionReferenceNumber) AS converted_auction
        WHERE judicial_bulletin.BulletinSearchId = ?
          AND converted_auction.AuctionReferenceNumber IS NOT NULL
          AND NOT EXISTS (
              SELECT 1
              FROM [ThirdParties].[BulletinAuctions] AS bulletin_auction
              WHERE bulletin_auction.AuctionReferenceNumber = converted_auction.AuctionReferenceNumber
          );
        """

    for auction in auctions:

        cursor.execute(query, auction.Auction, auction.Reference, bulletin_search_id)


def insert_judicial_bulletins(bulletins: list[BulletinAuction]):

    cursor = connection.cursor()
    query = """
        INSERT INTO [ThirdParties].[JudicialBulletins] (
            [JudicialBulletinId],
            [BulletinSearchId],
            [BulletinNumber]
        )
        SELECT
            ISNULL((SELECT MAX([JudicialBulletinId]) FROM [ThirdParties].[JudicialBulletins]), 0) + 1,
            ?,
            ?
        WHERE NOT EXISTS (
                SELECT 1
                FROM [ThirdParties].[JudicialBulletins] AS judicial_bulletin
                WHERE judicial_bulletin.BulletinSearchId = ?
                   OR judicial_bulletin.BulletinNumber = ?
            );
        """

    try:
        for bulletin in bulletins:

            cursor.execute(
                query,
                bulletin.BulletinSearchId,
                bulletin.BulletinNumber,
                bulletin.BulletinSearchId,
                bulletin.BulletinNumber,
            )

            insert_bulletin_auctions(bulletin.BulletinAuctions, bulletin.BulletinSearchId)

        connection.commit()

    except Exception:

        connection.rollback()
        raise
